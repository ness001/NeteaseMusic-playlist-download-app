import numpy as np
from tqdm import tqdm
result=0
test_num=100
for t in tqdm(range(0,test_num)):
    china_num = 10000
    year = 500
    for i in range(1,year+1):
        print('year: {}'.format(i))
        for china in range(1,china_num+1):
            if np.random.uniform(0,1,1)[0] <=0.03:
                china_num-=1
        print(china_num)
        '''35% 330 years'''
        if i == 330 & china_num>=1:
            result+=1
print(result/test_num)

# china_num = 10000
# year = 500
# for i in range(1, year + 1):
#     print('year: {}'.format(i))
#     for china in range(1, china_num + 1):
#         if np.random.uniform(0, 1, 1)[0] <= 0.03:
#             china_num -= 1
#     print(china_num)