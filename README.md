# FT225 Face Recognition Module
Simple Python code to test FT225 face recognition module

## Description
This module is quite cheap and available from AliExpress. It uses standard serial interface and can be quickly tried with Serial-to-USB converter. The really great point of this module its tiny size. It has two cameras to detect live/life face, so won't work on screenshots. It has `demo` mode so can detect any face, and therefore can be used as human presence/attention detector.

## Pinout
Black -> GND
Green -> RxD
Yellow -> TxD
Red -> Vcc

## Commands
You'll need to decipher Python code, but for a simplest setup you need only two commands:
'demo' - to enable demo mode
'verify` - to detect if there's a face

## Output
If module works and TxD and RxD are not mixed up, you'll get the following:
```
Please enter command: demo
Sending out command data: ef aa fe 00 01 01 fe
recv: REPLY size: 2
Operation Successful
Demo mode enabled successfully
mid: 254 result: 0  MR_SUCCESS(0): Operation successful reply_data:
Please enter command:
```

```
Please enter command: verify
Sending out command data: ef aa 12 00 02 00 0a 1a
recv: NOTE size: 17 
Face status: b'\x00\x00R\x00\xe6\x00"\x01\xdc\x01\xf9\xff\n\x00\x00\x00'
state: 0 left: 82 top: 230 right: 290 bottom: 476 yaw: -7 pitch: 10 roll: 0
Face status: OK
recv: REPLY size: 38 
Operation Successful
Verify successful
uid: 65535, username: , isadmin: 0, unlockstatus: 200
mid: 18 result: 0  MR_SUCCESS(0): Operation successful reply_data: ffff000000000000000000000000000000000000000000000000000000000000000000c8
```

## Credits
Original code is from manufacturer support board, which I was able to discover with help of ChatGpt. As manufacturer support virtuallu non existent outside of China, I went through their demo code, translated from Chinese and added some extra from datasheet.
