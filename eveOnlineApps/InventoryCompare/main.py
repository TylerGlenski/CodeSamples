import re

# some for fun eve online video game python coding, playing with regex. 
# the giant text field is an inventory copied from the video game
# still in development.


def text_parse(payload=''):
    
    my_str = ''
    str_arr = []
    index = 0
    my_str = ''
    str_regex = "^[A-Za-z0-9_-]*$"
    num_regex = '^[0-9]+$'
    index = 0
    return_value = {}
    for c in payload:
        if re.match(str_regex, c) or c =='-':
            if c != '\n':
                if payload[index-2] == '-':
                    if re.match(num_regex,c):
                        s = c + payload[index+1]
                        print(s) 
                        if s == '54':
                            if payload[index+2]:
                                s += payload[index+2]
                        my_str += s
                        # print(f"gas type")
                my_str += c

            
        index +=1 # do last lol
        
    

    # print(payload)
       
    print(f"{my_str}")

            
        



def main():
    print()
    # text_parse('''Fullerite-C321156 HarvestableCloud 5780m32089350932ISK Fullerite-C540250HarvestableCloud2500m31487884000ISK''')
    text_parse(f'''
        Fullerite-C32	1,156	Harvestable Cloud			5,780 m3	20,893,509.32 ISK
        Fullerite-C540	250	Harvestable Cloud			2,500 m3	14,878,840.00 ISK
        Fullerite-C60	4,649	Harvestable Cloud			4,649 m3	14,205,158.97 ISK
        Fullerite-C70	10,186	Harvestable Cloud			10,186 m3	41,718,494.62 ISK
        Fullerite-C72	6,287	Harvestable Cloud			12,574 m3	64,918,367.47 ISK
        Fullerite-C84	3,917	Harvestable Cloud			7,834 m3	31,127,772.28 ISK
        Helium Fuel Block	290	Fuel Block			1,450 m3	7,385,128.40 ISK
        Hydrogen Fuel Block	185	Fuel Block			925 m3	4,964,746.95 ISK
        Isogen	292,900	Mineral			2,929 m3	15,178,078.00 ISK
        Mexallon	150	Mineral			1.50 m3	25,930.50 ISK
        Morphite	250	Mineral			2.50 m3	16,138,735.00 ISK
        Nitrogen Fuel Block	390	Fuel Block			1,950 m3	10,387,692.90 ISK
        Nocxium	8,000	Mineral			80 m3	15,327,440.00 ISK
        Oxy-Organic Solvents Reaction Formula	1	Composite Reaction Formulas			0.01 m3	10,000,000.00 ISK
        Oxygen Fuel Block	158	Fuel Block			790 m3	4,414,252.98 ISK
        Platinum Technite Reaction Formula	2	Composite Reaction Formulas			0.02 m3	20,000,000.00 ISK
        Pyerite	72,282	Mineral			722.82 m3	1,827,288.96 ISK
        Reinforced Carbon Fiber Reaction Formula	2	Composite Reaction Formulas			0.02 m3	40,000,000.00 ISK
        Thermosetting Polymer Reaction Formula	1	Composite Reaction Formulas			0.01 m3	10,000,000.00 ISK
        Tritanium	40,641	Mineral			406.41 m3	266,604.96 ISK''')




if __name__ == "__main__":
   main()