# -*- coding: utf-8 -*-
import binascii
import struct
import ipaddr


class PslTyp:
    def __init__(self, cmd_id, name):
        self.cmd_id = cmd_id
        self.name = name

    def get_id(self):
        return self.cmd_id

    def get_name(self):
        return self.name

    def pack_py(self, value):
        raise NotImplementedError

    def unpack_py(self, value):
        raise NotImplementedError

    def pack_cmd(self, value):
        raise NotImplementedError

    def unpack_cmd(self, value):
        raise NotImplementedError

    def print_result(self, value):
        print "%-30s%s" % (self.get_name(). capitalize(), value)

    def is_setable(self):
        return True

    def is_queryable(self):
        return True

###############################################################################


class PslTypString(PslTyp):

    def pack_py(self, value):
        return value

    def unpack_py(self, value):
        return value

    def pack_cmd(self, value):
        return value

    def unpack_cmd(self, value):
        return value

###############################################################################
class PslTypPassword(PslTypString):
    def __init__(self, cmd_id, name, setable):
        PslTypString.__init__(self, cmd_id, name)
        self.setable = setable

    def is_queryable(self):
        return False

    def is_setable(self):
        return self.setable


################################################################################

class PslTypBoolean(PslTyp):

    def pack_py(self, value):
        if (value):
            return struct.pack(">b", 0x01)
        else:
            return struct.pack(">b", 0x00)

    def unpack_py(self, value):
        return (value == 0x01)

    def pack_cmd(self, value):
        return self.pack_py(value.lowercase == "on")

    def unpack_cmd(self, value):
        if (self.unpack_py(value)):
            return "on"
        else:
            return "off"


###############################################################################
class PslTypAction(PslTypBoolean):

    def pack_py(self, value):
        return struct.pack(">b", 0x01)

    def is_queryable(self):
        return False

################################################################################

class PslTypMac(PslTyp):

    def pack_py(self, val):
        if (len(val) == 17):
            return binascii.unhexlify(val[0:2]+val[3:5]+val[6:8]+
                                      val[9:11]+val[12:14]+val[15:17])
        if (len(val) == 12):
            return binascii.unhexlify(val)
        raise "unkown mac format="+val

    def unpack_py(self, value):
        mac = binascii.hexlify(value)
        return (mac[0:2]+":"+mac[2:4]+":"+mac[4:6]+":"+mac[6:8]+
               ":"+mac[8:10]+":"+mac[10:12])

    def pack_cmd(self, value):
        return self.pack_py(self, value)

    def unpack_cmd(self, value):
        return self.unpack_py(self, value)

################################################################################

class PslTypIpv4(PslTyp):

    def pack_py(self, value):
        i = (int)(ipaddr.IPv4Address(value))
        return struct.pack(">I", i)

    def unpack_py(self, value):
        adr = struct.unpack(">I", value)[0]
        return "%s" % ipaddr.IPv4Address(adr)

    def pack_cmd(self, value):
        return self.pack_py(self, value)

    def unpack_cmd(self, value):
        return self.unpack_py(self, value)

################################################################################

class PslTypHex(PslTyp):

    def pack_py(self, value):
        return binascii.unhexlify(value)

    def unpack_py(self, value):
        return binascii.hexlify(value)

    def pack_cmd(self, value):
        return self.pack_py(self, value)

    def unpack_cmd(self, value):
        return self.unpack_py(self, value)
################################################################################

class PslTypEnd(PslTypHex):

    def is_setable(self):
        return False

    def is_queryable(self):
        return False


################################################################################

class PslTypSpeedStat(PslTyp):
    SPEED_NONE = 0x00
    SPEED_10MH = 0x01
    SPEED_10ML = 0x02
    SPEED_100MH = 0x03
    SPEED_100ML = 0x04
    SPEED_1G = 0x05

    def unpack_py(self, value):
        rtn = {
            "port":struct.unpack(">b", value[0])[0],
            "speed":struct.unpack(">b", value[1])[0],
            "rest":binascii.hexlify(value[2:]),
        }
        return rtn

    def is_setable(self):
        return False
    
    def print_result(self, value):
        print "%-30s%4s%15s%10s" % ("Speed Statistic:", "Port", 
                                    "Speed", "FIXME")
        for row in value:
            speed = row["speed"]
            if speed == PslTypSpeedStat.SPEED_NONE:
                speed = "Not conn."
            if speed == PslTypSpeedStat.SPEED_10MH:
                speed = "10 Mbit/s H"
            if speed == PslTypSpeedStat.SPEED_10ML:
                speed = "10 Mbit/s L"
            if speed == PslTypSpeedStat.SPEED_100MH:
                speed = "100 Mbit/s H"
            if speed == PslTypSpeedStat.SPEED_100ML:
                speed = "100 Mbit/s L"
            if speed == PslTypSpeedStat.SPEED_1G:
                speed = "1 Gbit/s"
            print "%-30s%4d%15s%10s" % ("", row["port"], speed, row["rest"])


################################################################################

class PslTypPortStat(PslTyp):
        
    def unpack_py(self, val):
        rtn = {
            "port":struct.unpack(">b",val[0])[0],
            "rec":struct.unpack(">Q",val[1:9])[0],
            "send":struct.unpack(">Q",val[10:18])[0],
            "rest":binascii.hexlify(val[19:]),
        }
        return rtn

    def is_setable(self):
        return False
    
    def print_result(self, value):
        print "%-30s%4s%15s%15s %s" % ("Port Statistic:", "Port",
                                      "Rec.", "Send", "FIXME")
        for row in value:
            print "%-30s%4d%15d%15d %s" % ("", row["port"], row["rec"],
                                          row["send"], row["rest"])

################################################################################

class PslTypBandwith(PslTyp):

    def unpack_py(self, value):
        rtn = {
            "port":struct.unpack(">b", value[0])[0],
            "limit":struct.unpack(">h", value[3::])[0],
            "rest":binascii.hexlify(value[1:2]),
        }
        return rtn

################################################################################

class PslTypVlanId(PslTyp):

    def unpack_py(self, value):
        rtn = {
            "port":struct.unpack(">b",value[0])[0],
            "id":struct.unpack(">h",value[1:])[0],
        }
        return rtn