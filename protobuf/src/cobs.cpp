
#include "cobs.h"

COBEncoder::COBEncoder(HardwareSerial serial, int bs) {
	s = serial;
	buffsize = bs;
	bufpos = 0;
}

bool COBEncoder::decode(char byte) {
	if (bufpos == 0) {
		next0 = byte;
		bufpos++;
		return false;
	}

	// This is the end of a packet
	if (byte == 0) {
		// assert(buffpos == next0);
		return true;
	}

	// According to our previous pointer, this byte should be 0
	if (bufpos == next0) {
		next0 = byte;
		buff[bufpos++] = 0;
	}

	return false;
}

int COBEncoder::available(char *msg) {
	while (s.available()) {
		if (COBEncoder::decode(s.read())) {
			msg = (char*)malloc(bufpos);
			if (!msg) {
				return 0;
			}

			memcpy(msg, &buff, bufpos);
			return bufpos;
		}
	}

	return NULL;
}
