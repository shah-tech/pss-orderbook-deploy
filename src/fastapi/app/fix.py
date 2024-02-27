from dataclasses import dataclass
import datetime
from multiprocessing import Queue
import json
import logging
import pandas as pd


@dataclass
class FixMessages:

    client: str = "WILEY"
    broker: str = "MS"
    client_seq_number: int = 1
    broker_seq_number: int = 1
    is_login: bool = False

    def log(self, msg): # this is overriden in children class
        print(msg)


    def new_order(self, stock: str="AAPL", qty: int = 1, order_id: int=1, side: int=1, price: float=1.0 ):

        """
        params
        ------
            side: 1 is buy, 2 is sell
        """

        # new order receive
        self.log(f"8=FIX4.4; 35=D; 34={self.client_seq_number}; 49={self.client}; 56={self.broker}; 52={datetime.datetime.now()};"+
                f" 55={stock}; 40=2; 38={qty}; 21=2; 11={order_id}{datetime.datetime.now().strftime('%Y-%m-%d')};"+
                f" 60={datetime.datetime.now()}; 54={side}; 44={price}; 10=0252;")


        # new order acknowledge
        self.log(f"8=FIX4.4; 35=8; 34={self.broker_seq_number}; 49={self.broker}; 56={self.client}; 52={datetime.datetime.now()};"+
                f" 55={stock}; 40=2; 21=2; 11={order_id}{datetime.datetime.now().strftime('%Y-%m-%d')};"+
                f" 32=0; 17=exec{datetime.datetime.now()}; 38={qty}; 60={datetime.datetime.now()}; 54={side}; "+
                f"44={price}; 6=0; 14=0; 37={order_id}{datetime.datetime.now().strftime('%Y-%m-%d')}; 10=200;")

        self.broker_seq_number +=1
        self.client_seq_number +=1

        # connect to DB, see if a pending order

    def partial_fill(self, stock="AAPL", order_id=1, price=1, side=1, qty=1, last_order_qty=1, cum_qty=1):
        # 150=1 is partial fill
        PARTIALFILL=f"8=FIX4.4; 35=8; 34={self.broker_seq_number}; 49={self.broker}; 56={self.client}; 52={datetime.datetime.now()}; "+ \
        f"55={stock}; 40=2; 11={order_id}{datetime.datetime.now().strftime('%Y-%m-%d')}; 31={price}; 39=1; 54={side}; 44={price}; 32={last_order_qty}; 17=exec{datetime.datetime.now()}; "+\
                        f"38={qty}; 60={datetime.datetime.now()}; 6={price}; 14={cum_qty}; 37={order_id}{datetime.datetime.now().strftime('%Y-%m-%d')} 10=240;"
        self.broker_seq_number +=1
        self.log(PARTIALFILL)

    def full_fill(self, stock="AAPL", order_id=1, price=1, side=1, qty=1):
        FULLYFILLED=f"8=FIX4.4; 35=8; 34={self.broker_seq_number}; 49={self.broker}; 56={self.client}; "+\
        f"52={datetime.datetime.now()}; 55={stock}; 40=2; 11={order_id}{datetime.datetime.now().strftime('%Y-%m-%d')}; "+\
        f"31={price}; 39=2; 54={side}; "+\
        f"44={price}; 32=0; 17=exec{datetime.datetime.now()}; 38={qty}; 60={datetime.datetime.now()}; 6={price}; 14={qty}; 37={order_id}; 10=246;"
        self.broker_seq_number +=1
        self.log(FULLYFILLED)

    def cancel_order(self, qty_remaining=1, stock="AAPL", order_id=1, side=1, qty=1, cum_qty=1):
        # 39=4 is cancled
        CANCELACK=f"8=FIX4.4; 35=8; 34={self.broker_seq_number}; 49={self.broker}; 56={self.client}; 52={datetime.datetime.now()}; 151={qty_remaining}; "+\
                        f"55={stock}; 11=C_{order_id}; 31=0; 39=4; 54={side}; 17=exec{datetime.datetime.now()}; 32=0;  41={order_id}; 38={qty}; "+\
                        f"60={datetime.datetime.now()};  6=0.0; 14={cum_qty}; 37={order_id}; 10=252;"
        self.log(CANCELACK)

    def login(self):
        self.log(f"8=FIX4.4; 35=A; 34={self.client_seq_number}; 49={self.client}; 56={self.broker}; 52={datetime.datetime.now()}; 108=30; 10=0015;")
        self.log(f"8=FIX4.4; 35=A; 34={self.broker_seq_number}; 49={self.broker}; 56={self.client}; 52={datetime.datetime.now()}; 108=30; 10=0016;")
        self.is_login=True

    def heartbeat(self):

        if not self.is_login:
            return None

        self.client_seq_number+=1
        self.broker_seq_number+=1

        self.log(f"8=FIX4.4; 35=0; 34={self.client_seq_number}; 49={self.client}; 56={self.broker}; 52={datetime.datetime.now()}; 108=30; 10=0015;")
        self.log(f"8=FIX4.4; 35=0; 34={self.broker_seq_number}; 49={self.broker}; 56={self.client}; 52={datetime.datetime.now()}; 108=30; 10=0015;")






@dataclass
class FixDecoder(FixMessages):

    tags: dict = None

    def __init__ (self):
        self.tags = json.load(open('app/fix.4.4.decode.json'))

    def fix_to_dict(self, msg):
        fix_dict = {}
        codes = msg.split(";")
        for code in codes:
            try: key, value = code.split("=")
            except: continue
            key, value = self.fix_decode(key.replace(" ", ""), value.replace(" ", ""))
            fix_dict[key]=value
        return fix_dict


    def fix_decode(self, key, value):


        try: name = self.tags[key]['name']
        except : name = key

        try: val = self.tags[key]['values'][value]
        except: val = value

        return name, val

@dataclass
class Fix(FixDecoder):

    logDir: str = "/logs-volume/fixlogs/"
    logName: str = "fixlog"
    logExt: str = ".log"
    #logDateExt: str = "%Y-%m-%d-%H-%M" # %Y-%m-%d for new log file daily, %Y-%m-%d-%H hourly, %Y-%m-%d-%H-%M minute
    # eg /logs-volume/fixlog2022-01-01-10-20.log
        
    def __init__(self):
        self.logger = logging.getLogger('fix')
        super().__init__()

    def log(self, msg_data: str=""):

        # log to logfile()
        #open(self.logfile(),'a').write(msg_data+"\n")

        # log og message to loki
        self.logger.info(
            json.dumps(msg_data),
            extra={ 'tags': {'type':"fixlogs"}}
        )

        # log tranlated fix to loki
        self.logger.info(
            json.dumps(self.fix_to_dict(msg_data)),
            extra={'tags':{'type':"fixlogs-decoded"}}
        )

    def logfile(self) -> str:
        """
        function returns a string of the current file to write fix logs too

        """
        return f'{self.logDir}{self.logName}{self.logExt}'
