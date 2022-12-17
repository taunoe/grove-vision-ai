# https://forum.seeedstudio.com/t/vision-ai-module/267388
import smbus2 as smbus
import time

#features
FEATURE_SYSTEM = 0x80
FEATURE_ALGO = 0xA0

#commands
CMD_SYS_READ_STATE = 0x03
CMD_SYS_STATE_LENGTH = 0x01

CMD_SYS_RESET = 0x20

CMD_ALGO_INOVKE = 0xA0
CMD_ALGO_READ_RET_LEN = 0xA1
CMD_ALGO_READ_RET_LEN_LENGTH = 0x02

CMD_ALGO_WRITE_ALGO = 0x01
CMD_ALGO_WRITE_MODEL = 0x11
CMD_ALGO_WRITE_CONFIDENCE = 0x41

CMD_ALGO_CONFIG_SAVE = 0xEE

CMD_STATE_IDLE = 0x00
CMD_STATE_RUNNING = 0x01
CMD_STATE_ERROR = 0x02

ALGO_OBJECT_DETECTION = 0
ALGO_OBJECT_COUNT = 1
ALGO_IMAGE_CLASSIFICATION = 2

MODEL_PRE_INDEX_1 = 0x00
MODEL_PRE_INDEX_2 = 0x01
MODEL_PRE_INDEX_3 = 0x02
MODEL_PRE_INDEX_4 = 0x03
MODEL_EXT_INDEX_1 = 0x10
MODEL_EXT_INDEX_2 = 0x11
MODEL_EXT_INDEX_3 = 0x12
MODEL_EXT_INDEX_4 = 0x13

FOUR_BYTES = 0x04

CMD_SYS_READ_ID = 0x02
CMD_SYS_ID_LENGTH = 2
CMD_SYS_READ_VERSION = 0x01
CMD_SYS_VERSION_LENGTH = 2
CMD_ALGO_READ_ALGO = 0x00
CMD_ALGO_ALGO_LENGTH = 0x01
CMD_ALGO_READ_MODEL = 0x10
CMD_ALGO_MODEL_LENGTH = 0x01
CMD_ALGO_READ_CONFIDENCE = 0x40
CMD_ALGO_CONFIDENCE_LENGTH = 0x01

GROVE_AI_CAMERA_ID = 0x0100


class VisionAI(object):
    def __init__(self, bus=1, address=0x62):
        self.bus = smbus.SMBus(bus)
        self.address = address
        self.algo_confidence = 50
 
    def read_data(self, data, num_of_bytes):
        time.sleep(0.005)
        write = smbus.i2c_msg.write(self.address, data)
        self.bus.i2c_rdwr(write)
        time.sleep(0.005)
        read = smbus.i2c_msg.read(self.address, num_of_bytes)
        self.bus.i2c_rdwr(read)
        if (num_of_bytes == 1):
            return list(read)[0]
        return list(read)

    def read_data_big_endian(self, data, num_of_bytes):
        time.sleep(0.005)
        write = smbus.i2c_msg.write(self.address, data)
        self.bus.i2c_rdwr(write)
        time.sleep(0.005)
        read = smbus.i2c_msg.read(self.address, num_of_bytes)
        self.bus.i2c_rdwr(read)
        return sum(list(read)[-(i+1)]<<(8*i) for i, _ in enumerate(read))  # buf[0]<<8*2 | buf[1]<<8*1 | buf[2]
    
    def write_data(self, data):
        time.sleep(0.005)
        write = smbus.i2c_msg.write(self.address, data)
        self.bus.i2c_rdwr(write)

    def get_result_len(self):
        return self.read_data([FEATURE_ALGO,CMD_ALGO_READ_RET_LEN],CMD_ALGO_READ_RET_LEN_LENGTH)

    def state(self):
        return self.read_data([FEATURE_SYSTEM,CMD_SYS_READ_STATE],CMD_SYS_STATE_LENGTH)

    def config_save(self):
        self.write_data([FEATURE_ALGO,CMD_ALGO_CONFIG_SAVE])
        while(1):
            ret = self.state()
            print('Config save state:',ret)    #Debug
            if (ret == CMD_STATE_IDLE):
                return True
            elif (ret == CMD_STATE_ERROR):
                print('Config save failed')
                return False

    def reset(self):
        self.write_data([FEATURE_SYSTEM,CMD_SYS_RESET])
        time.sleep(0.5)

    def begin(self, algo, model, confidence):
        error_count = 0
        
        try:
            self.system_id = visionAI.read_data_big_endian([FEATURE_SYSTEM,CMD_SYS_READ_ID],CMD_SYS_ID_LENGTH)
            if (GROVE_AI_CAMERA_ID != self.system_id):
                print('Not matching ID. Expected:',GROVE_AI_CAMERA_ID,'Received:',self.system_id)
                return False

            self.system_version = visionAI.read_data_big_endian([FEATURE_SYSTEM,CMD_SYS_READ_VERSION],CMD_SYS_VERSION_LENGTH)

            self.algo_algo = visionAI.read_data([FEATURE_ALGO,CMD_ALGO_READ_ALGO],CMD_ALGO_ALGO_LENGTH)
            self.algo_model = visionAI.read_data([FEATURE_ALGO,CMD_ALGO_READ_MODEL],CMD_ALGO_MODEL_LENGTH)
            self.algo_confidence = visionAI.read_data([FEATURE_ALGO,CMD_ALGO_READ_CONFIDENCE],CMD_ALGO_CONFIDENCE_LENGTH)

            if (algo != self.algo_algo or model != self.algo_model or confidence != self.algo_confidence):
                self.write_data([FEATURE_ALGO,CMD_ALGO_WRITE_ALGO,algo])
                self.write_data([FEATURE_ALGO,CMD_ALGO_WRITE_MODEL,model])
                self.write_data([FEATURE_ALGO,CMD_ALGO_WRITE_CONFIDENCE,confidence])
                self.algo_algo = visionAI.read_data([FEATURE_ALGO,CMD_ALGO_READ_ALGO],CMD_ALGO_ALGO_LENGTH)
                self.algo_model = visionAI.read_data([FEATURE_ALGO,CMD_ALGO_READ_MODEL],CMD_ALGO_MODEL_LENGTH)
                self.algo_confidence = visionAI.read_data([FEATURE_ALGO,CMD_ALGO_READ_CONFIDENCE],CMD_ALGO_CONFIDENCE_LENGTH)
                if (algo != self.algo_algo):
                    print('Not matching Algo. Expected:',algo,'Received:',self.algo_algo)
                    error_count += 1
                if (model != self.algo_model):
                    print('Not matching Model. Expected:',model,'Received:',self.algo_model)
                    error_count += 1
                if (confidence != self.algo_confidence):
                    print('Not matching Confidence. Expected:',confidence,'Received:',self.algo_confidence)
                    error_count += 1
                if (error_count != 0):
                    return False
                if (not self.config_save()):
                    return False
                self.reset()

        except OSError as e:
            if (e.errno == 5):
                print('Model unknown')
            if (e.errno == 121):
                print('Reset Grove Vision AI Module')
            print(OSError.__name__,':',e)
            exit()

        return True

    def invoke(self):
        self.write_data([FEATURE_ALGO,CMD_ALGO_INOVKE])
        while(1):
            ret = self.state()
            print('Invoke state:',ret)     #Debug
            if (ret == CMD_STATE_RUNNING):
                return True
            elif (ret == CMD_STATE_ERROR):
                print('Invoke failed') 
                return False


if __name__ == "__main__":
    visionAI = VisionAI()

    print('Address:',visionAI.address)
    
    if (not visionAI.begin(ALGO_OBJECT_COUNT, MODEL_PRE_INDEX_1, 45)):    #Bis jetzt geht nur MODEL_PRE_INDEX_1
        print('Algo begin failed')
    
    print('Version:',visionAI.system_version)
    print('ID:',visionAI.system_id)
    print('Algo:',visionAI.algo_algo)
    print('Model:',visionAI.algo_model)
    print('Confidence:',visionAI.algo_confidence)

    if (visionAI.invoke()):
        while(1):
            ret = visionAI.state()
            if (ret == CMD_STATE_IDLE):
                break
            time.sleep(0.02)
        print('People detected: ',visionAI.get_result_len())
    