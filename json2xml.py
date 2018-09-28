# from src.json2xml import Json2xml
# data = Json2xml.fromjsonfile('./0.json').data
# data_object = Json2xml(data)
# d = data_object.json2xml() #xml output
# savename = '0.xml'
# f = open(savename, 'w')
# f.write(d)
# f.close()

import json
import glob

s1="""    <object>
        <name>{0}</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>{1}</xmin>
            <ymin>{2}</ymin>
            <xmax>{3}</xmax>
            <ymax>{4}</ymax>
        </bndbox>
    </object>"""

s2="""<annotation>
    <folder>VOC2007</folder>
    <filename>{0}</filename>
    <source>
        <database>My Database</database>
        <annotation>VOC2007</annotation>
        <image>flickr</image>
        <flickrid>NULL</flickrid>
    </source>
    <owner>
        <flickrid>NULL</flickrid>
        <name>J</name>
    </owner>
    <size>
        <width>3840</width>
        <height>2160</height>
        <depth>3</depth>
    </size>
    <segmented>0</segmented>
    <object>
        <name>{1}</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>{2}</xmin>
            <ymin>{3}</ymin>
            <xmax>{4}</xmax>
            <ymax>{5}</ymax>
        </bndbox>
    </object>{6}
</annotation>
"""

#if __name__ == '__main__':
filepath = ('./')
txt = []

for i in range(1, 453):

    if(i<10):
        readimg = '0000' +str(i)
    elif(i<100):
        readimg = '000' +str(i)
    elif(i<1000):
        readimg = '00' +str(i)
    else:
        readimg = '0' +str(i)

    filename_read = filepath + readimg + '.json'

    with open(filename_read) as f:
        data = json.load(f)
        shapes = data['shapes']   #output shapes which include: 'line_color' 'label' 'fill_color' 'points'
        # print(shapes)
        #result = json.dumps(path,ensure_ascii=False) #output image name with string like "0.jpg"
        
        #read state and the 4 labels of points
        ob2 = ""
        for item in shapes:  #read 'label' and 'points'
            state_tmp = item['label']
            name = "state" + str(state_tmp)  #get the state string
            #print(item['points'][1])
            xmin = item['points'][0][0]
            ymin = item['points'][0][1]
            xmax = item['points'][2][0]
            ymax = item['points'][2][1]
            #print(xmin,ymin,xmax,ymax)
            ob2+='\n' + s1.format(name, xmin, ymin, xmax, ymax)

        #output imagname.jpg and savename.xml with 0 forward
        if(i<10):
            imgname = '0000' +str(i) + '.jpg'
            savename = '0000' +str(i) + '.xml'
        elif(i<100):
            imgname = '000' +str(i) + '.jpg'            
            savename = '000' +str(i) + '.xml'
        elif(i<1000):
            imgname = '00' +str(i) + '.jpg'
            savename = '00' +str(i) + '.xml'
        else:
            imgname = '0' +str(i) + '.jpg'
            savename = '0' +str(i) + '.xml'

        print(imgname,savename)
        f = open(savename, 'w')
        ob1=s2.format(imgname, name, xmin, ymin, xmax, ymax, ob2)
        f.write(ob1)
        f.close()

    txt.append(readimg+'\n')

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




