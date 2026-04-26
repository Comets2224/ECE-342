import serial
import numpy as np
import time
import pyqtgraph

NUM_SAMPLES = 1250
TOTAL_BYTES = NUM_SAMPLES * 4
total_bytes_read = 0
wave0 = None
wave1 = None

serial_obj = serial.Serial('COM7', 6000000, timeout=10)
print(f"Port: {serial_obj.name} @ {serial_obj.baudrate} baud")

factor = 3.3 / ((2**10) - 1)

start = time.perf_counter()

while total_bytes_read < TOTAL_BYTES:

    serial_obj.reset_input_buffer()
    serial_obj.write(b'\x01')
    serial_obj.flush()

    raw = serial_obj.read(TOTAL_BYTES)
    total_bytes_read += len(raw)

    samples = np.frombuffer(raw, dtype='<u2')
    wave0 = samples[0::2] * factor
    wave1 = samples[1::2] * factor

    #graph.setData(wave0)

end = time.perf_counter()

print(f"[TEST COMPLETE] {total_bytes_read} bytes ({total_bytes_read / 4} samples) read in {end - start:.6f} s")

serial_obj.close()

graph = pyqtgraph.plot(y=wave0, pen='y')
graph.plot(y=wave1, pen='c')

pyqtgraph.exec()
