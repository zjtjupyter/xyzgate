


txt = []
for i in range(0,300):
	txt.append(str(i)+'\n')

for j in range(1,2113):
	if(j<10):
		imgname_0 = '0000' +str(j)
		imgname_1 = '1000' +str(j)
		imgname_2 = '2000' +str(j)
	elif(j<100):
		imgname_0 = '000' +str(j)
		imgname_1 = '100' +str(j)
		imgname_2 = '200' +str(j)
	elif(j<1000):
		imgname_0 = '00' +str(j)
		imgname_1 = '10' +str(j)
		imgname_2 = '20' +str(j)
	else:
		imgname_0 = '0' +str(j)
		imgname_1 = '1' +str(j)
		imgname_2 = '2' +str(j)

	if j<435:
		txt.append(imgname_0+'\n')
		txt.append(imgname_1+'\n')
		#txt.append(imgname_2+'\n')
	elif j<453:
		txt.append(imgname_0+'\n')
		txt.append(imgname_1+'\n')
		txt.append(imgname_2+'\n')
	elif j<1948:
		txt.append(imgname_1+'\n')
		txt.append(imgname_2+'\n')
	else:
		txt.append(imgname_2+'\n')
ftxt_1 = open("./test.txt", 'w')
ftxt_2 = open("./train.txt", 'w')
ftxt_3 = open("./trainval.txt", 'w')
ftxt_4 = open("./val.txt", 'w')
ftxt_1.writelines(txt)
ftxt_2.writelines(txt)
ftxt_3.writelines(txt)
ftxt_4.writelines(txt)
ftxt_1.close()
ftxt_2.close()
ftxt_3.close()
ftxt_4.close()

