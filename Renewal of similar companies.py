#필요한 라이브러리 import
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import io
import numpy as np
import pandas as pd
import warnings
from sklearn.preprocessing import StandardScaler
from collections import Counter

warnings.filterwarnings(action='ignore')

#거리 기반으로 유사도 측정하여 가장 유사한 K개의 기업을 뽑음
def classify_knn(inX, feature, labels, K, feature_list):
    #유클리드 거리 계산 과정
    dists = feature - inX
    result = dists[:, 0]
    for i in range(1, len(feature_list)):
        result += dists[:, i] ** 2
    dists = np.array(np.sqrt(result))

    #거리 짧은 순대로 정렬
    sorted_index = np.argsort(dists)
    K_nearest_labels = []

    # 가까운 k개의 기업의 사업자등록번호 추출
    for index in sorted_index:
        K_nearest_labels.append(labels.iloc[index]['사업자등록번호'])
        if len(list(set(K_nearest_labels))) >= K: break
    return K_nearest_labels

#정규화를 진행하는 함수
def standard_data(feature_list, input_list, features):
    # 입력값을 포함하여 거리계산을 하기 위해 값을 정규화 하기 위한 과정
    input_dict = {name: value for name, value in zip(feature_list, input_list)}
    input_df = pd.DataFrame(input_dict, index=[0])
    feature_scalar = features.append(input_df)
    feature_scalar.reset_index(drop=True, inplace=True)

    feature_scalar = StandardScaler().fit_transform(feature_scalar)
    #정규화한 후 입력값과 나머지 데이터를 분리하여 반환
    return feature_scalar[-1], feature_scalar[:-1]

#데이터 세서 자르는 함수
def count_data(company, recomend_num, select_column):
    count_money = company.loc[:, select_column]
    c = Counter(count_money)
    keys = [name for name, count in c.most_common(recomend_num)]
    values = [c[name] for name, count in c.most_common(recomend_num)]
    return keys

class MyApp(QMainWindow):
    def __init__(self):   #초기화 함수
        super().__init__()
        self.initUI()
        self.sector = ' ' #업종
        self.person = 0  #종업원수
        self.run_days = 0 #사업년수
        self.property = 0 #금년도 자산총계
        self.lproperty = 0 #전년도 자산총계
        self.capital = 0 #자본총계
        self.profit = 0  #영업이익
        self.sales = 0 #매출액
        self.pure = 0 #순이익

    def initUI(self):
        # 메뉴바 추가
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('Menu')

        # Save 버튼 추가
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S') #단축키 설정
        save_action.triggered.connect(self.save) #버튼을 눌렀을 때 save 함수로 연결

        # Clear 버튼 추가
        clear_action = QAction('Clear', self)
        clear_action.setShortcut('Ctrl+C') #단축키 설정
        clear_action.triggered.connect(self.clear) #버튼을 눌렀을 때 clear 함수로 연결

        # 제목 추가
        self.title = QLabel('Serprise!', self)
        self.title.resize(400, 100)
        self.title.move(340, 100)  # 제목 위치 x = 340, y = 100

        # 제목 폰트, 사이즈 설정
        font1 = self.title.font()
        font1.setFamily('Times New Roman')
        font1.setPointSize(50)
        font1.setBold(True)
        self.title.setFont(font1)

        # 프로그램 title 설정
        self.setWindowTitle('Serprise SERVICE')
        # 프로그램 사이즈 설정
        self.resize(1000, 800)


        ##########################################
        # 기업 정보 입력 칸
        # 종업원 수
        self.text1 = QLabel(self)
        self.text1.resize(200,30)
        self.text1.move(100,350)
        self.text1.setText('종업원수를 입력하시오!')

        self.line1 = QLineEdit(self)
        self.line1.resize(200,30)
        self.line1.move(300,350)

        # 사업년수
        self.text2 = QLabel(self)
        self.text2.resize(200, 30)
        self.text2.move(100, 400)
        self.text2.setText('사업년수를 입력하시오!')

        self.line2 = QLineEdit(self)
        self.line2.resize(200, 30)
        self.line2.move(300, 400)

        # 전년도 자산총계
        self.text3 = QLabel(self)
        self.text3.resize(200, 30)
        self.text3.move(100, 450)
        self.text3.setText('작년 자산총계를 입력하시오!')

        self.line3 = QLineEdit(self)
        self.line3.resize(200, 30)
        self.line3.move(300, 450)

        # 금년도 자산총계
        self.text4 = QLabel(self)
        self.text4.resize(200, 30)
        self.text4.move(100, 500)
        self.text4.setText('올해 자산총계를 입력하시오!')

        self.line4 = QLineEdit(self)
        self.line4.resize(200, 30)
        self.line4.move(300, 500)

        # 금년도 매출액
        self.text5 = QLabel(self)
        self.text5.resize(200, 30)
        self.text5.move(510, 350)
        self.text5.setText('올해 매출액을 입력하시오!')

        self.line5 = QLineEdit(self)
        self.line5.resize(200, 30)
        self.line5.move(710, 350)

        # 금년도 자본총계
        self.text6 = QLabel(self)
        self.text6.resize(200, 30)
        self.text6.move(510, 400)
        self.text6.setText('올해 자본총계를 입력하시오!')

        self.line6 = QLineEdit(self)
        self.line6.resize(200, 30)
        self.line6.move(710, 400)

        # 금년도 순이익
        self.text7 = QLabel(self)
        self.text7.resize(200, 30)
        self.text7.move(510, 450)
        self.text7.setText('올해 순이익를 입력하시오!')

        self.line7 = QLineEdit(self)
        self.line7.resize(200, 30)
        self.line7.move(710, 450)

        # 금년도 영업이익
        self.text8 = QLabel(self)
        self.text8.resize(200, 30)
        self.text8.move(510, 500)
        self.text8.setText('올해 영업이익을 입력하시오!')

        self.line8 = QLineEdit(self)
        self.line8.resize(200, 30)
        self.line8.move(710, 500)

        # 업종
        self.text9 = QLabel(self)
        self.text9.resize(200, 30)
        self.text9.move(250, 550)
        self.text9.setText('기업의 업종을 선택하시오!')

        self.cb = QComboBox(self)
        self.cb.addItem('선택하시오')
        self.cb.addItem('제조업')  # C
        self.cb.addItem('건설업')  # F
        self.cb.addItem('도매업')  # G
        self.cb.move(550, 550)
        self.cb.currentTextChanged.connect(self.comobobox_select)

        self.text10 = QLabel(self)
        self.text10.resize(100,30)
        self.text10.move(350,250)
        self.text10.setText('사업자등록번호\n(10자리)')

        self.line9 = QLineEdit(self)
        self.line9.resize(80,30)
        self.line9.move(450,250)

        self.button2 = QPushButton(self)
        self.button2.resize(200, 30)
        self.button2.move(550,250)
        self.button2.setText('사업자 등록번호로 찾아오기')
        self.button2.clicked.connect(self.Get_Company_Registration_Number)

        #기업 정보 입력 완료 버튼
        self.button = QPushButton(self)
        self.button.resize(200, 30)
        self.button.move(400, 650)
        self.button.setText('내 기업 정보 입력 완료!')
        self.button.clicked.connect(self.buttonPressEvent)

        #팀이름
        self.text7 = QLabel(self)
        self.text7.resize(350, 30)
        self.text7.move(340, 750)
        self.text7.setText('빅리더 AI 아카데미 한국고용정보원 - 잡포유 팀')

        #유사기업 계산 완료 표시
        self.text11 = QLabel(self)
        self.text11.resize(120, 30)
        self.text11.move(460, 700)

        #메뉴에 save, clear 추가
        filemenu.addAction(save_action)
        filemenu.addAction(clear_action)

        self.statusBar = self.statusBar()
        self.show()

    ##############################################
    # 연결 함수

    def comobobox_select(self,e):
        #콤보 박스에 선택된 업종을 대분류 코드로 매핑
        self.tmp = self.cb.currentText()
        if self.tmp == '제조업':  #제조업
            self.sector = 'C'
        elif self.tmp == '건설업':  #건설업
            self.sector = 'F'
        elif self.tmp == '도매업':  #도매업
            self.sector = 'G'
        else:  #선택하시오
            self.sector = ' '

# 내 기업 정보 입력완료 변수를 누르면 입력된 값들 출력
    def buttonPressEvent(self,e):
        # 입력되어있는 변수를 저장
        self.person = self.line1.text()  # 종업원수
        self.run_days = self.line2.text()  # 사업년수
        self.property = self.line3.text()  # 금년도 자산총계
        self.lproperty = self.line4.text()  # 전년도 자산총계
        self.sales = self.line5.text()  # 매출액
        self.capital = self.line6.text()  # 자본총계
        self.pure = self.line7.text()  # 순이익
        self.profit = self.line8.text()  # 영업이익

        self.string = (
                    '종업원수 ' + self.person + '명 ' + '사업년수 ' + self.run_days + '년 ' + '올해 자산총계 ' + self.property + '원 ' + '업종 : ' + self.sector + ' ' +
                    '자본총계 : ' + self.capital + ' 영업이익 : ' + self.profit + ' 매출액 : ' + self.sales)

        print(self.string)

        # 장려금에 대해서 몇개의 기업을 참고할 것인지 지정
        k_money = 20
        recomend_num_money = 7
        # 훈련데이터에 대해서 몇개의 기업을 참고할 것인지 지정
        k_train = 29
        recomend_num_train = 10

        # 입력
        input_dict = {}
        input_dict['통합종업원수'] = self.person
        input_dict['사업년도'] = self.run_days
        input_dict['전년도_자산총계'] = self.lproperty  # 전년도 자산총계
        input_dict['자산총계_2022'] = self.property
        input_dict['업종코드_세세분류'] = self.sector
        input_dict['자본총계'] = self.capital
        input_dict['영업이익'] = self.profit
        input_dict['매출액'] = self.sales

        # 장려금 정보에 대한 유사기업 찾는 과정
        df_kodata_money = pd.read_excel('./../data/kodata+장려금(중복제거,받은기업들만).xlsx')
        # 유사기업을 뽑을 특징값 x 목록
        feature_list_money = ['통합종업원수', '사업년도', '자산총계_2022']

        input_list = []
        for i in feature_list_money:
            input_list.append(input_dict[i])

        features = df_kodata_money.loc[
            df_kodata_money['업종코드_세세분류'].str[0] == input_dict['업종코드_세세분류'], feature_list_money]

        # 라벨값 y
        label_list = '사업자등록번호'
        labels = df_kodata_money[[label_list]]

        input_list, feature = standard_data(feature_list_money, input_list, features)

        # 넘파이 배열로 변경
        inX = np.array(input_list)

        # k개의 유사기업 사업자등록번호 뽑아내기
        company = df_kodata_money.loc[df_kodata_money[label_list].isin(classify_knn(inX, feature, labels, k_money, feature_list_money)), :]
        # 개수로 상위를 뽑을 열을 선택
        select_column = '상위 정책서비스 명'
        # 뽑아낸 유사기업의 데이터를 구분
        keys = count_data(company, recomend_num_money, select_column)

        df_kodata_money.loc[
            (df_kodata_money[label_list].isin(company[label_list])) & df_kodata_money[select_column].isin(
                keys), '그룹'] = 1

        df_kodata_money.loc[(df_kodata_money.loc[
                                 df_kodata_money['업종코드_세세분류'].str[0] == input_dict['업종코드_세세분류'], label_list].isin(
            company[label_list])) & df_kodata_money[select_column].isin(keys), '그룹'] = 1

        # 저장
        df_kodata_money.to_excel('./../장려금예시.xlsx', index=False)

        # --- 훈련 대하여
        df_kodata_train = pd.read_excel('./../data/훈련명 추가_220828.xlsx')
        feature_list_train = ['통합종업원수', '사업년도', '자산총계_2022']

        input_list = []
        for i in feature_list_train:
            input_list.append(input_dict[i])

        # 유사기업을 뽑을 특징값 x 목록
        features = df_kodata_train.loc[
            df_kodata_train['업종코드_세세분류'].str[0] == input_dict['업종코드_세세분류'], feature_list_train]

        # 라벨값 y
        label_list = '사업자등록번호'
        labels = df_kodata_train[[label_list]]

        input_list, feature = standard_data(feature_list_train, input_list, features)

        # 넘파이 배열로 변경
        inX = np.array(input_list)

        # k개의 유사기업 사업자등록번호 뽑아내기
        company = df_kodata_train.loc[df_kodata_train[label_list].isin(classify_knn(inX, feature, labels, k_train, feature_list_train)), :]
        # 개수로 상위를 뽑을 열을 선택
        select_column = 'KECO 코드'
        # 뽑아낸 유사기업의 데이터를 구분
        keys = count_data(company, recomend_num_train, select_column)
        df_kodata_train.loc[
            (df_kodata_train[label_list].isin(company[label_list])) & df_kodata_train[select_column].isin(
                keys), '그룹'] = 1

        df_kodata_train.loc[(df_kodata_train.loc[
                                 df_kodata_train['업종코드_세세분류'].str[0] == input_dict['업종코드_세세분류'], label_list].isin(
            company[label_list])) & df_kodata_train[select_column].isin(keys), '그룹'] = 1
        # 저장
        df_kodata_train.to_excel('./../훈련예시.xlsx', index=False)



        # 유사기업이 분류되는 모든 작업이 끝났음을 명시
        self.text11.setText('유사기업 설정 완료')


    def Get_Company_Registration_Number(self,e):
        #입력된 사업자 번호로 데이터를 불러와서 채우기
        df = pd.read_excel('./../data/kodata+장려금(중복제거,받은기업들만).xlsx')
        temp = df.loc[df['사업자등록번호'] == int(self.line9.text()),:]
        temp = temp.iloc[0,:]

        if temp['업종코드_세세분류'][0] == 'C' :  #제조업
            self.cb.setCurrentIndex(1)  # 업종
        elif temp['업종코드_세세분류'][0] == 'F' :  #건설업
            self.cb.setCurrentIndex(2)  # 업종
        elif temp['업종코드_세세분류'][0] == 'G' :  #도매업
            self.cb.setCurrentIndex(3)  # 업종
        self.line1.setText(str(temp['통합종업원수']))  # 종업원수
        self.line2.setText(str(temp['사업년도']))  # 사업년수
        self.line3.setText(str(temp['자산총계_2022']))  # 금년도 자산총계
        self.line4.setText(str(temp['자산총계_2021']))  # 전년도 자산총계
        self.line5.setText(str(temp['매출액_2022']))  # 매출액
        self.line6.setText(str(temp['자본총계_2022']))  # 자본총계
        self.line7.setText(str(temp['당기순손익_2022']))  # 순이익
        self.line8.setText(str(temp['영업이익_2022']))  # 영업이익

# 입력한 정보를 변수에 저장
    def save(self):
        # self.sector = self.cb.currentText()  # 업종
        self.person = self.line1.text()  # 종업원수
        self.run_days = self.line2.text()  # 사업년수
        self.property = self.line3.text()  # 금년도 자산총계
        self.lproperty = self.line4.text()  # 전년도 자산총계
        self.sales = self.line5.text()  # 매출액
        self.capital = self.line6.text()  # 자본총계
        self.pure = self.line7.text()  # 순이익
        self.profit = self.line8.text()  # 영업이익

# clear 버튼 누르면 입력정보를 초기화 시키는 함수
    def clear(self):
        self.sector = ' '  # 업종
        self.person = 0  # 종업원수
        self.run_days = 0  # 사업년수
        self.property = 0  # 금년도 자산총계
        self.lproperty = 0  # 전년도 자산총계
        self.capital = 0  # 자본총계
        self.profit = 0  # 영업이익
        self.sales = 0  # 매출액
        self.pure = 0  # 순이익

        self.sector = self.cb.setCurrentIndex(0)  # 업종
        self.person = self.line1.setText(' ') # 종업원수
        self.run_days = self.line2.setText(' ') # 사업년수
        self.property = self.line3.setText(' ') # 금년도 자산총계
        self.lproperty = self.line4.setText(' ') # 전년도 자산총계
        self.sales = self.line5.setText(' ') # 매출액
        self.capital = self.line6.setText(' ')  # 자본총계
        self.pure = self.line7.setText(' ') # 순이익
        self.profit = self.line8.setText(' ')  # 영업이익



#####################################
# 실행
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
