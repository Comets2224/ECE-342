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

print(f"\n=====  Connected to: {serial_obj.name} at {serial_obj.baudrate} baud  =====\n")
print("When sampling has begun, press CTRL+C to stop sampling.\n")
print("During sampling, nominal current should be observed.")
input("\n=====  Press any key to signal the Teensy to begin sampling.  =====")

factor = 3.3 / ((2**10) - 1)

start = time.perf_counter()
end = time.perf_counter()

while end - start < 1.0:

    serial_obj.reset_input_buffer()
    serial_obj.write(b'\x01')
    serial_obj.flush()

    raw = serial_obj.read(TOTAL_BYTES)
    total_bytes_read += len(raw)

    samples = np.frombuffer(raw, dtype='<u2')
    wave0 = samples[0::2] * factor
    wave1 = samples[1::2] * factor

    end = time.perf_counter()
    print(f"{total_bytes_read} bytes ({total_bytes_read / 4} samples) read and converted in {end - start:.6f} s")
    #graph.setData(wave0)

print(f"\n[TEST COMPLETE] {total_bytes_read} bytes ({total_bytes_read / 4} samples) read in {end - start:.6f} s")
print(f"Per-Channel Sampling Frequency: ~{(total_bytes_read / 4) / (end - start):.0f} Hz")

input("Press enter to write to the provided flash drive, peak current should be expected.")
serial_obj.write(b'\x03')

serial_obj.close()

print(f"\nTest graph is generating...")
graph = pyqtgraph.plot(y=wave0, pen='y')
graph.plot(y=wave1, pen='c')

pyqtgraph.exec()
