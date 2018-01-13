#-*-coding:utf-8-*-

province_to_town_to_district = {
        'guangdong':{'guangzhou':['huadu','panyu'],'qingyuan':['shipai','wng']},
        'zhejiang':{'hangzhou':['xihu'],}
}

status = {}
while True:
    if "province" not in status.keys() or status['province'] == '':
        print province_to_town_to_district.keys()
        choice = raw_input("input choice:")
        
        if choice == 'e':
            print "exiting"
            break
        
        if choice not in province_to_town_to_district.keys():
            print "wrong province choice"
        status['province'] = choice
    elif  "town" not in status.keys() or status['town'] == '':
        print province_to_town_to_district[status['province']]
        choice = raw_input("input choice:")
        
        if choice == 'e':
            print "exiting"
            break        
        
        if choice not in province_to_town_to_district[status['province']].keys():
            if choice == 'b':
                status['province'] = ''
                continue
            else:
                print "wrong town choice"
        status['town'] = choice
    elif "district" not in status.keys() or status['district'] == '':
        print province_to_town_to_district[status['province']][status['town']]
        choice = raw_input("input choice:")
        if choice == 'e':
            print "exiting"
            break        
        
        if choice not in province_to_town_to_district[status['province']][status['town']]:
            if choice == 'b':
                status['town'] = ''
                continue
            else:
                print "wrong district choice"
        status['district'] = choice
    else:
        info = ''' status:
            province:%s
            town:%s
            district:%s
        ''' % (status['province'],status['town'],status['district'])
        print info
        choice = raw_input("continue??,y/n/b/e:")
        if choice == "n" or choice == 'e':
            print "exiting..."
            break
        elif choice == "y":
            continue
        elif choice == 'b':
            status['district'] = ''
        else:
            print "wrong choice"
    
