import time
import serial

def read_sensor_data(port='COM5', baud_rate=115200):
    try:
        # Membuka koneksi ke port serial
        with serial.Serial(port, baud_rate, timeout=2) as ser:
            if ser.is_open:
                ser.flushInput()  # Membersihkan buffer input
                time.sleep(0.1)   # Beri waktu sejenak untuk inisialisasi
                
                while True:  # Terus baca hingga mendapatkan data yang valid
                    # Membaca data dari sensor
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        # Cek apakah data berisi angka dan koma
                        if all(c.isdigit() or c == '.' or c == ',' for c in line):
                            # Asumsi data berupa: "34.52,80.00,34.94"
                            data = line.split(',')
                            if len(data) == 3:  # Pastikan ada 3 elemen data
                                heart_rate = float(data[0])  # Gunakan float jika ada desimal
                                oxygen_saturation = float(data[1])
                                temperature = float(data[2])
                                
                                # Validasi nilai
                                if heart_rate > 0 and oxygen_saturation > 0 and temperature != 0:
                                    return heart_rate, oxygen_saturation, temperature
                        else:
                            print(f"Received non-numeric data: {line}")
    except serial.SerialException as e:
        print(f"Serial exception: {e}")
        return None, None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None, None
