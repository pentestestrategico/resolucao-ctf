# OT/SCADA

`se03-modbus.pcap`, `lit-iec104.pcap`, `clm-dnp3.pcap` (pcaps reais; tshark).

## Modbus (se03-modbus.pcap)
```bash
tshark -r se03-modbus.pcap -Y 'tcp.port==502' -T fields -e ip.dst | sort|uniq -c   # 10.60.10.31
tshark -r se03-modbus.pcap -Y 'modbus.func_code==6 && ip.src==10.50.10.88' -x       # unit1 fc6 ref9c91(40081) val35e8(13800)
tshark -r se03-modbus.pcap -Y 'modbus.func_code==17' -T fields -e modbus.data       # Report Slave ID
# 25 43005400... -> len 0x25, UTF-16LE "CTF{ICG4200-unit1}"
```

## IEC 60870-5-104 (lit-iec104.pcap)
```bash
tshark -r lit-iec104.pcap -Y 'iec60870_asdu.typeid==45' -T fields -e iec60870_asdu.causetx -e iec60870_asdu.ioa -e iec60870_asdu.addr -e ip.dst
# C_SC_NA_1 TypeId 45, COT 6 (act), IOA 2451, ASDU addr 3, dst 10.80.20.40
tshark -r lit-iec104.pcap -Y 'iec60870_asdu.typeid==136' -x   # UTF-16LE CTF{c_sc_na-2451}
```

## DNP3 (clm-dnp3.pcap)
```bash
tshark -r clm-dnp3.pcap -Y 'dnp3.al.func==4' -T fields -e dnp3.dst -e dnp3.src -e dnp3.al.obj -e dnp3.al.index
# Operate: dst 50, src 14, func 4, obj 0x0c01 (CROB), index 7
tshark -r clm-dnp3.pcap -Y 'dnp3.al.func==129 && dnp3.al.obj==0x4300' -x   # reassembled UTF-16LE CTF{crob-idx7}
```
