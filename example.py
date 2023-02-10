from honeywell_hsc_i2c.hsc_i2c import honeywell_hsc

hsc_i2c = honeywell_hsc(0x28)

print(hsc_i2c.get_pressure())
