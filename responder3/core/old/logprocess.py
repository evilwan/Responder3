import os
from abc import ABC, abstractmethod
import threading
import multiprocessing
import logging

from responder3.core.common import *

"""
logqueue = {
        'host':'127.0.0.1',
        'port': 50001,
        'authkey': None,
}
"""

class LogProcessor(multiprocessing.Process):
        def __init__(self, logsettings):
                multiprocessing.Process.__init__(self)
                self.logsettings = logsettings
                self.resultQ     = None
                self.logger      = None
                self.extensionsQueues = []
                self.resultHistory = {}


        def log(self, level, message):
                self.handleLog(LogEntry(level, self.name, message))

        def setup(self):
                import importlib
                #SETTING UP LOGQUEUE
                self.resultQ = get_logQueue()
                logging.config.dictConfig(self.logsettings['log'])
                for handler in self.logsettings['handlers']:
                        try:
                                handlerclassname  = '%sHandler' % self.logsettings['handlers'][handler]
                                handlermodulename = 'responder3_log_%s' % handler.replace('-','_').lower()
                                handlermodulename = '%s.%s' % (handlermodulename, handlerclassname)
                                
                                self.log(logging.DEBUG,'Importing handler module: %s , %s' % (handlermodulename,handlerclassname))
                                handlerclass = getattr(importlib.import_module(handlermodulename), handlerclassname)

                        except Exception as e:
                                self.log(logging.ERROR,'Error importing module %s Reason: %s' % (handlermodulename, e) )
                                continue

                        try:
                                tqueue = multiprocessing.Queue()
                                self.extensionsQueues.append(tqueue)
                                self.log(logging.DEBUG,'Lunching extention handler: %s' % (handlerclassname,))
                                hdl = handlerclass(tqueue, self.resultQ, self.logsettings[self.logsettings['handlers'][handler]])
                                hdl.start()
                        except Exception as e:
                                self.log(logging.ERROR,'Error creating class %s Reason: %s' % (handlerclassname, e) )
                                continue
        
        def run(self):
                self.setup()                
                self.log(logging.INFO,'setup done')
                #while not self.stopEvent.is_set():
                while True:
                        resultObj = self.resultQ.get()
                        if isinstance(resultObj, Result):
                                self.handleResult(resultObj)
                        elif isinstance(resultObj, LogEntry):
                                self.handleLog(resultObj)
                        elif isinstance(resultObj, Connection):
                                self.handleConnection(resultObj)
                        elif isinstance(resultObj, EmailEntry):
                                self.handleEmail(resultObj)
                        elif isinstance(resultObj, PoisonResult):
                                self.handlePoisonResult(resultObj)
                        else:
                                raise Exception('Unknown object in queue! Got type: %s' % type(resultObj))

        def handleLog(self, log):
                logging.log(log.level, str(log))

        def handleConnection(self, con):
                logging.log(logging.INFO, str(con))
                t = {}
                t['type'] = 'Connection'
                t['data'] = con.toDict()
                for tqueue in self.extensionsQueues:
                        tqueue.put(t)

        def handleResult(self, result):
                logging.log(logging.INFO, str(result.toDict()))
                if result.fingerprint not in self.resultHistory:
                        self.resultHistory[result.fingerprint] = result
                        t = {}
                        t['type'] = 'Result'
                        t['data'] = result.toDict()
                        for tqueue in self.extensionsQueues:
                                tqueue.put(t)
                else:
                        self.log(logging.INFO,'Duplicate result found! Filtered.')

        def handleEmail(self, email):
                if 'writePath' in self.logsettings['email']:
                        folder = Path(self.logsettings['email']['writePath'])
                        filename = 'email_%s.eml' % str(uuid.uuid4())

                        with open(str(folder.joinpath(filename).resolve()), 'wb') as f:
                                f.write(email.email.as_bytes())
                
                self.log(logging.INFO,'You got mail!')

        def handlePoisonResult(self, poisonResult):
                self.log(logging.INFO,repr(poisonResult))

class LoggerExtension(ABC, threading.Thread):
        def __init__(self, resQ, logQ, config):
                threading.Thread.__init__(self)
                self.resQ = resQ
                self.logQ = logQ
                self.config = config
                self.logname = '%s-%s' % ('LogExt',self.modulename())
                

        def log(self, level, message):
                self.logQ.put(LogEntry(level, self.logname, message))

        def run(self):
                self.init(self.config)
                self.setup()
                self.log(logging.DEBUG,'Started!')
                self.main()
                self.log(logging.DEBUG,'Exiting!')

        @abstractmethod
        def init(self, config):
                pass

        @abstractmethod
        def main(self):
                pass

        @abstractmethod
        def modulename(self):
                pass

        @abstractmethod
        def setup(self):
                pass