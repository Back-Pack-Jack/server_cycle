a = ['TEST', 1623606392.099296, 'SPS30', {'PM1.0': 1.3130239486694335, 'PM2.5': 1.3884735226631164, 'PM4.0': 1.3884743213653565, 'PM10': 1.3884743213653565, 'N_PM0.5': 8.85998854637146, 'N_PM1.0': 10.435381937026978, 'N_PM2.5': 10.479040956497192, 'N_PM4.0': 10.481891584396362, 'N_PM10': 10.483817100524902, 'avg_size': 0.4452741503715515}]
b = ['TEST', 1623606392.1014476, 'MICS6814', [{'OXIDISING': 176592.40097472497}, {'REDUCING': 45563.465109040684}, {'NH3': 110451.683340548}, {'ADC': 3.2300512820512814}]]
c = ['TEST', 1623606392.102347, 'ZMOD4510', [{'Rmox[0]': 50343.9605}, {'Rmox[1]': 887.6260000000002}, {'Rmox[2]': 633.3454999999999}, {'Rmox[3]': 617.6529999999999}, {'Rmox[4]': 610.0735000000002}, {'Rmox[5]': 601.237}, {'Rmox[6]': 601.4065}, {'Rmox[7]': 598.3485}, {'O3_conc_ppb': 0.0}, {'Fast AQI': 0.0}, {'EPA AQI': 0.0}]]

def in_data(indata):
    if indata[2] == 'SPS30':
        print(indata[3]['PM1.0'])
        print(indata[3]['PM2.5'])
        print(indata[3]['PM4.0'])
        print(indata[3]['PM10'])
        print(indata[3]['N_PM0.5'])
        print(indata[3]['N_PM1.0'])
        print(indata[3]['N_PM2.5'])
        print(indata[3]['N_PM4.0'])
        print(indata[3]['N_PM10'])
        print(indata[3]['avg_size'])

    if indata[2] == 'MICS6814':
        print(indata[2])
    if indata[2] == 'ZMOD4510':
        print(indata[2])

in_data(a)