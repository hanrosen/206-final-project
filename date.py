def date_conversion(date):
    split = date.split()
    year = str(date.split()[-1])
    if "January" in date:
        month = '01'
        if len(split[1]) == 4:
            day = '0' + split[1][0]
            release = "{}-{}-{}".format(month, day, year)
        else:
            day = split[1][:2]
        release = "{}-{}-{}".format(month, day, year)
    elif "February" in date:
        split = date.split()
        month = '02'
        if len(split[1]) == 4:
            day = '0' + split[1][0]
            release = "{}-{}-{}".format(month, day, year)
        else:
            day = split[1][:2]
        release = "{}-{}-{}".format(month, day, year)

    elif "March" in date:
        split = date.split()
        month = '03'
        if len(split[1]) == 4:
            day = '0' + split[1][0]
            release = "{}-{}-{}".format(month, day, year)
        else:
            day = split[1][:2]
        release = "{}-{}-{}".format(month, day, year)
    elif "April" in date:
        split = date.split()
        month = '04'
        if len(split[1]) == 4:
            day = '0' + split[1][0]
            release = "{}-{}-{}".format(month, day, year)
        else:
            day = split[1][:2]
        release = "{}-{}-{}".format(month, day, year)
    elif "May" in date:
        split = date.split()
        month = '05'
        if len(split[1]) == 4:
            day = '0' + split[1][0]
            release = "{}-{}-{}".format(month, day, year)
        else:
            day = split[1][:2]
        release = "{}-{}-{}".format(month, day, year)
    elif "June" in date:
        split = date.split()
        month = '06'
        if len(split[1]) == 4:
            day = '0' + split[1][0]
            release = "{}-{}-{}".format(month, day, year)
        else:
            day = split[1][:2]
        release = "{}-{}-{}".format(month, day, year)
    elif "July" in date:
        split = date.split()
        month = '07'
        if len(split[1]) == 4:
            day = '0' + split[1][0]
            release = "{}-{}-{}".format(month, day, year)
        else:
            day = split[1][:2]
        release = "{}-{}-{}".format(month, day, year)
    elif "August" in date:
        split = date.split()
        month = '08'
        if len(split[1]) == 4:
            day = '0' + split[1][0]
            release = "{}-{}-{}".format(month, day, year)
        else:
            day = split[1][:2]
        release = "{}-{}-{}".format(month, day, year)
    elif "September" in date:
        split = date.split()
        month = '09'
        if len(split[1]) == 4:
            day = '0' + split[1][0]
            release = "{}-{}-{}".format(month, day, year)
        else:
            day = split[1][:2]
        release = "{}-{}-{}".format(month, day, year)
    elif "October" in date:
        split = date.split()
        month = '10'
        if len(split[1]) == 4:
            day = '0' + split[1][0]
            release = "{}-{}-{}".format(month, day, year)
        else:
            day = split[1][:2]
        release = "{}-{}-{}".format(month, day, year)
    elif "November" in date:
        split = date.split()
        month = '11'
        if len(split[1]) == 4:
            day = '0' + split[1][0]
            release = "{}-{}-{}".format(month, day, year)
        else:
            day = split[1][:2]
        release = "{}-{}-{}".format(month, day, year)
    elif "December" in date:
        split = date.split()
        month = '12'
        if len(split[1]) == 4:
            day = '0' + split[1][0]
            release = "{}-{}-{}".format(month, day, year)
        else:
            day = split[1][:2]
        release = "{}-{}-{}".format(month, day, year)
    # else:
    #     release = None
    return release

date_conversion("December 12nd, 2017")
