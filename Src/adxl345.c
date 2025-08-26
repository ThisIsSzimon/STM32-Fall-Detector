#include "adxl345.h"

uint8_t data_rec[6];
uint8_t chipid=0;
char x_char[3], y_char[3], z_char[3];
#define adxl_address 0x53<<1
extern I2C_HandleTypeDef hi2c2;

void adxl_write (uint8_t reg, uint8_t value)
{
	uint8_t data[2];
	data[0] = reg;
	data[1] = value;
	HAL_I2C_Master_Transmit (&hi2c2, adxl_address, data, 2, 10);
}

void adxl_read (uint8_t reg, uint8_t numberofbytes)
{
	HAL_I2C_Mem_Read (&hi2c2, adxl_address, reg, 1, data_rec, numberofbytes, 100);
}


void adxl_init (void)
{
	adxl_read (0x00, 1); // czyta DEVID - sprawdza czy sie komunikuje
	adxl_write (0x2d, 0); //reset wszystich bitow
	adxl_write (0x2d, 0x08);
	adxl_write (0x31, 0x09); //tutaj ustawiamy czułość
	adxl_write(0x2C, 0x0A); // 100 Hz, normalny tryb
}

void adxl_read_xyz(int16_t *x, int16_t *y, int16_t *z)
{
    uint8_t data[6];
    HAL_I2C_Mem_Read(&hi2c2, adxl_address, 0x32, 1, data, 6, 100);

    *x = (int16_t)((data[1] << 8) | data[0]);
    *y = (int16_t)((data[3] << 8) | data[2]);
    *z = (int16_t)((data[5] << 8) | data[4]);
}

