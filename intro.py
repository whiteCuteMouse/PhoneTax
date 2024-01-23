import streamlit as st
import pandas as pd
import re
import altair as alt
st.write("Hello!")
#pd.set_option('display.max_columns', None) #df 출력 시 모든 열 출력
#pd.set_option('display.max_rows', None) #df 출력 시 모든 행 출력
#pd.reset_option("display") display option 초기화
#%%
#페이지에 관한 정보
try:
   st.set_page_config(
      page_title="포넷택스 팀 챗봇 데이터 분석 및 시각화: 대시 보드",
      page_icon="📊",
      layout="wide",#centered가 기본값. 고정 너비 안에 element들을 제한. wide는 화면 전체를 사용함.
      initial_sidebar_state="expanded")
except:
   pass
PRIMARY_COLOR = "#872434"
#html <p>에 글씨 쓰기
def p_write(txt, font_size = 10, font_weight = "normal", text_align = "center", font_style = "normal", color = "black", writeHTML=True):
    r = f'<p style="font-family:Malgun Gothic; text-align:{text_align}; font-size: {font_size}px; font-weight: {font_weight}; font-style: {font_style}; color: {color}">{txt}</p>'
    if writeHTML:
        st.markdown(r, unsafe_allow_html=True)
    return r
#html <span>에 글씨 쓰기
#span에는 text-align 속성이 없음
def span_write(txt, font_size = 10, font_weight = "normal", font_style = "normal", color = "black", writeHTML = True):
    r = f'<span style="font-family:Malgun Gothic; font-size: {font_size}px; font-weight: {font_weight}; font-style: {font_style}; color: {color}">{txt}</span>'
    if writeHTML:
        st.markdown(r, unsafe_allow_html=True)
    return r

#st.title("*포넷택스* 대시 보드")
title1 = span_write("포넷택스", 40, "bold", "italic", PRIMARY_COLOR, writeHTML=False)
title2 = span_write(" 대시보드", 40, "bold", "normal", writeHTML=False)
st.markdown(f'{title1}{title2}', unsafe_allow_html=True)
#st.markdown('<span style="font-family:Malgun Gothic; font-size: 44px; font-weight: bold; font-style: italic; color: #872434">포넷택스</span><span style="font-family:Malgun Gothic; font-size: 44px; font-weight: bold"> 대시보드</span>', unsafe_allow_html=True)
#%%
#데이터 로딩 및 초기화

def str_to_timedelta(str_t):
    if type(str_t) == str:
        s = re.search(r"(\d+)[h]\s*(\d+)[m]\s*(\d+)[s]", str_t)
        
        return pd.Timedelta(hours=int(s.group(1)), minutes=int(s.group(2)), seconds=int(s.group(3)))
    else:#결측치인 경우 넘어가기
        return #pd.Timedelta(hours=int(s.group(0)), minutes=int(s.group(0)), seconds=int(s.group(0)))

# 세 파일의 sheet들을 각각 합치기
#@st.cache_data
def load_data():
    fnames = ["2022.01.01~2022.06.30챗봇데이터.xlsx", "2022.07.01~2022.12.31.xlsx", "2023.01.01~2023.06.30.xlsx"]


    df_UserChat = pd.DataFrame([])
    df_User = pd.DataFrame([])
    df_Message = pd.DataFrame([])
    df_UserChatTag = pd.DataFrame([])
    
    for fname in fnames:
        sheet_UserChat = pd.read_excel(fname, engine = 'openpyxl', sheet_name = 'UserChat data')
        sheet_User = pd.read_excel(fname, engine = 'openpyxl', sheet_name = 'User data')
        sheet_Message = pd.read_excel(fname, engine = 'openpyxl', sheet_name = 'Message data')
        sheet_UserChatTag = pd.read_excel(fname, engine = 'openpyxl', sheet_name = 'UserChatTag data')
        
        df_UserChat = pd.concat([df_UserChat, sheet_UserChat], axis=0, ignore_index=True) #axis=0로 행 방향(세로) 결합
        df_User = pd.concat([df_User, sheet_User], axis=0, ignore_index=True)
        df_Message = pd.concat([df_Message, sheet_Message], axis=0, ignore_index=True)
        df_UserChatTag = pd.concat([df_UserChatTag, sheet_UserChatTag], axis=0, ignore_index=True)
    
    #날짜 데이터 형식 변환(대소 비교 등을 위해)
    #df_User와 나머지의 날짜 형식이 다름!
    try:
        df_User['lastSeenAt'] = pd.to_datetime(df_User['lastSeenAt'], format='%Y-%m-%dT%H:%M:%S.%fZ', infer_datetime_format=True)#infer_datetime_format=True는 pandas가 자동으로 형식 추론
    except:#여기에만 형식 안 맞는 거 하나 있음
        df_User['lastSeenAt'] = pd.to_datetime(df_User['lastSeenAt'], format='%Y-%m-%dT%H:%M:%S.%dZ', infer_datetime_format=True)#infer_datetime_format=True는 pandas가 자동으로 형식 추론
    df_User['updatedAt'] = pd.to_datetime(df_User['updatedAt'], format='%Y-%m-%dT%H:%M:%S.%fZ', infer_datetime_format=True)
    df_User['createdAt'] = pd.to_datetime(df_User['createdAt'], format='%Y-%m-%dT%H:%M:%S.%fZ', infer_datetime_format=True)
    df_User['web.lastSeenAt'] = pd.to_datetime(df_User['web.lastSeenAt'], format='%Y-%m-%dT%H:%M:%S.%fZ', infer_datetime_format=True)
    
    
    df_Message['createdAt'] = pd.to_datetime(df_Message['createdAt'], format='%Y-%m-%d %H:%M:%S', infer_datetime_format=True)
    df_UserChatTag['UserChatTag data'] = pd.to_datetime(df_UserChatTag['createdAt'], format='%Y-%m-%d %H:%M:%S', infer_datetime_format=True)
    
    df_UserChat['firstOpenedAt'] = pd.to_datetime(df_UserChat['firstOpenedAt'], format='%Y-%m-%dT%H:%M:%S.%fZ', infer_datetime_format=True)
    df_UserChat['openedAt'] = pd.to_datetime(df_UserChat['openedAt'], format='%Y-%m-%dT%H:%M:%S.%fZ', infer_datetime_format=True)
    df_UserChat['firstRepliedAtAfterOpen'] = pd.to_datetime(df_UserChat['firstRepliedAtAfterOpen'], format='%Y-%m-%dT%H:%M:%S.%fZ', infer_datetime_format=True)
    df_UserChat['createdAt'] = pd.to_datetime(df_UserChat['createdAt'], format='%Y-%m-%dT%H:%M:%S.%fZ', infer_datetime_format=True)
    df_UserChat['closedAt'] = pd.to_datetime(df_UserChat['closedAt'], format='%Y-%m-%dT%H:%M:%S.%fZ', infer_datetime_format=True)
    
    #UserChat 시트의 waitingTime 등등을 timedelta 형식으로 바꾸기
    df_UserChat['waitingTime'] = df_UserChat['waitingTime'].apply(str_to_timedelta)
    df_UserChat['avgReplyTime'] = df_UserChat['avgReplyTime'].apply(str_to_timedelta)
    df_UserChat['totalReplyTime'] = df_UserChat['totalReplyTime'].apply(str_to_timedelta)
    df_UserChat['resolutionTime'] = df_UserChat['resolutionTime'].apply(str_to_timedelta)
    df_UserChat['operationWaitingTime'] = df_UserChat['operationWaitingTime'].apply(str_to_timedelta)
    df_UserChat['operationAvgReplyTime'] = df_UserChat['operationAvgReplyTime'].apply(str_to_timedelta)
    df_UserChat['operationTotalReplyTime'] = df_UserChat['operationTotalReplyTime'].apply(str_to_timedelta)
    
    r = dict()
    r['UserChat'] = df_UserChat
    r['User'] = df_User
    r['Message'] = df_Message
    r['UserChatTag'] = df_UserChatTag
    return r

#로딩이 끝났으면 데이터 전처리
@st.cache_data
def data_init(dfs):
    # *************** df_User 전처리 ***************
    #print(df_User)
    # 중복된 User data의 행 없애기(id를 기준으로)
    dfs['User'] = dfs['User'].drop_duplicates(subset='id')
    
    # *************** df_UserChatTag 전처리 ***************
    # 중복된 UserChatTag data의 행 없애기(id를 기준으로)
    dfs['UserChatTag'] = dfs['UserChatTag'].drop_duplicates(subset='id')
    
    
    # *************** df_Message 전처리 ***************
    #날짜를 기준으로 df_Message 정렬
    dfs['Message'] = dfs['Message'].sort_values(by='createdAt')
    #print(len(set(dfs[2]['chatId']))) #4563
    
    #먼저 personType이 user인 행만 걸러내기
    dfs['Message'] = dfs['Message'][dfs['Message']['personType'] == 'user']
    #print(len(set(dfs[2]['chatId']))) #4547
    
    #실제 user인 행만 걸러내기(User에 등록된 id와 비교)
    #print(dfs[2][~dfs[2]['personId'].isin(set(dfs[1]['id']))])
    dfs['Message'] = dfs['Message'][dfs['Message']['personId'].isin(set(dfs['User']['id']))]
    #print(len(set(dfs[2]['chatId']))) #3917
    
    #df_UserChat 전처리 이후 df_Message 한 번 더 전처리 필요(서로의 chatId(df_UserChat은 id)가 서로에게 있는 것만 남김)
    
    # *************** df_UserChat 전처리 ***************
    #operationReplyCount를 기준으로 결측치 제거
    #print("제거 이전 수", len(set(dfs[0]['id'])))#4563개
    dfs['UserChat'] = dfs['UserChat'].dropna(subset=['operationReplyCount'])
    #print("제거 이후 수", len(set(dfs[0]['id']))) #제거 이후 3342
    
    #실제 채팅 내역 데이터(Message)랑 비교했을 땐 더 줄어듦 
    #df_Message에 chatId와 동일한 것만 걸러내기
    dfs['UserChat'] = dfs['UserChat'][dfs['UserChat']['id'].isin(set(dfs['Message']['chatId']))]
    #print("Message의 chatId와 겹치는 것만 개수", len(set(dfs[0]['id'])))#3688
    
    #taga열의 결측치는 '태그 없음'으로 처리
    dfs['UserChat']['tags'] = dfs['UserChat']['tags'].fillna('태그 없음')
    
    # df_Message 전처리2
    dfs['Message'] = dfs['Message'][dfs['Message']['chatId'].isin(set(dfs['UserChat']['id']))]
    
    #print(filtered_df_Message)
    
    #personType이 user인 것만 포함한 Message에 있는 chatId 개수보다 UserChat에 있는 id가 많음.
    #즉, Message의 chatId 수 < UserChat의 id 수
    #확인 결과 UserChat에는 있지만 Message에는 아예 없는 경우도 있고, manager라서 빠진 경우도 있음.
    #따라서 실제 user가 대화한 것으로 판단되는 것을 세려면 user만 포함한 Message에 있는 chatId를 세야 함.
    
    #UserChat과 Message의 수가 같아야 함
    #각각 2889개로 같음
    #print(len(set(dfs[0]['id'])), len(set(dfs[2]['chatId'])))
    
    return dfs

# Session Initialization
# 세션은 데이터를 전역 변수처럼 저장해 놓는 기능. 화면 조작을 할 때마다 파이썬 코드를 처음부터 실행하는데, 세션에 넣어두면 값 초기화를 건너뛸 수 있음.
# 주의: 캐시랑은 다른 개념!! 캐시는 자주 사용하는 값을 로드해 놓는 것인 반면(페이지 새로고침해도 남아 있음), 세션은 값을 연속성 있게 사용할 수 있도록(예: 로그인 상태 저장) 하는 것임.
# 캐시는 로컬에 저장, 세션은 서버 또는 클라이언트에 저장
if 'dfs' not in st.session_state:
    st.session_state['dfs'] = data_init(load_data())
    
dfs = st.session_state['dfs']
#데이터 로딩 및 초기화 끝
#화면 표시
#sidebar
with st.sidebar:
    st.header("표시 지정")
    show_all = st.toggle('생략 없이 모든 정보 표시')
    if show_all:
        st.write("현재 :red[***생략 없이 모든 정보를 표시***]하고 있습니다.")
    else:
        st.write("현재 전체 대비 :red[***5% 미만인 정보들을'기타'로 처리***]하고 있습니다.")
#%%
with st.container():#container은 화면상 가로로 나눔
    # 특정 열의 모든 Timestamp를 normalize하는 함수(normalize는 시, 분, 초 정보 지움)
    def normalize_timestamp(timestamp):
         return timestamp.normalize()
     
    #시, 분, 초 정보가 지워진 timestamp를 문자열로 만들기
    def convert_to_date_in_string(timestamp):
        return timestamp.strftime("%Y년 %m월 %d일")
    
    @st.cache_data
    def init_slider_data():
        #채팅의 가장 이른 날짜와 가장 늦은 날짜를 알아내기(UserChat 이용)
        #UserChat의 firstOpenedAt이 Message의 createdAt과 동일함.
        earliest_timestamp = dfs['UserChat']['firstOpenedAt'].min()
        latest_timestamp = dfs['UserChat']['firstOpenedAt'].max()
    
        # timestamp를 깊은 복사 후 normalize해서 시간, 분, 초 정보는 지우기
        opt = dfs['UserChat']['firstOpenedAt'].copy()
        opt = opt.apply(normalize_timestamp)
        
        #중복된 날짜 제거
        opt = opt.drop_duplicates()
        #timestamp를 문자열로 변환
        opt = opt.apply(convert_to_date_in_string)
        
        return earliest_timestamp, latest_timestamp, opt
    st.session_state['slider'] = init_slider_data()#슬라이더 관련 값은 세션에. 이건 계속 변하는 값이니까 if문 사용하지 않음.
    earliest_timestamp, latest_timestamp, opt = st.session_state['slider'][0], st.session_state['slider'][1], st.session_state['slider'][2]
    
    #start_date, end_date는 슬라이더에서 선택된 날짜 범위
    start_date, end_date = st.select_slider(
        '##### 데이터를 살펴볼 기간을 선택하세요',
        options=opt,#options는 슬라이더에 들어갈 수 있는 모든 값들(일 기준)
        value=(convert_to_date_in_string(earliest_timestamp), convert_to_date_in_string(latest_timestamp)), #value는 슬라이더의 양 끝 값
        key = "date_slider" #session에 date_slider라는 이름으로 등록
        )
    st.write(f'{start_date}' '부터', f'{end_date}' '까지의 데이터를 살펴봅니다.')
    start_timestamp = pd.to_datetime(start_date, format="%Y년 %m월 %d일")
    end_timestamp = pd.to_datetime(end_date, format="%Y년 %m월 %d일")
    end_timestamp = end_timestamp.replace(hour = 23, minute = 59, second = 59) #끝 날짜는 그 날짜의 마지막 시간으로 해야 함
#%%
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])#columns는 화면상 세로로 나눔 [1, 2, 1]은 1:2:1 비율로 나눈다는 뜻
    with col1:
        with st.container(border = True):
            #기간별 총 이용 건수 출력
            
            #슬라이더로 선택한 기간별 필터링된 dfs 만들기
            def filter_dfs(dfs):
                filtered_dfs = dict()
                
                filtered_dfs['UserChat'] = dfs['UserChat'][(dfs['UserChat']['firstOpenedAt'] >= start_timestamp) & (dfs['UserChat']['firstOpenedAt'] <= end_timestamp)]
                filtered_dfs['Message'] = dfs['Message'][(dfs['Message']['createdAt'] >= start_timestamp) & (dfs['Message']['createdAt'] <= end_timestamp)]
                return filtered_dfs
            
            st.session_state['filtered_dfs'] = filter_dfs(dfs)
            filtered_dfs = st.session_state['filtered_dfs']
            
            #기간 내 UserChat을 원본 데이터에서 걸러내기
            #UserChat의 firstOpenedAt이 Message의 createdAt과 동일함.
            #filtered_df_UserChat = dfs['UserChat'][(dfs['UserChat']['firstOpenedAt'] >= start_timestamp) & (dfs['UserChat']['firstOpenedAt'] <= end_timestamp)]
            
            
            #총 이용 건수 출력
            total_uses = filtered_dfs['UserChat'].shape[0]
            st.write("### 총 이용 건수")
            
            p_write(str(total_uses), 80, "bold", "center")
            #st.markdown('<p style="font-family:Malgun Gothic; text-align: center; font-size: 100px; font-weight: bold">'+f'{total_uses}'+'</p>', unsafe_allow_html=True)
        
        #%%
        with st.container(border = True):
            st.write("### 문의 유형별 건수")
            #우선 UserChat의 tag들을 뽑아내기
            #tag에는 하나 이상의 태그들이 있으므로, ', '(띄어쓰기 포함! 왜냐하면 [백로그]건의,제언처럼 태그 자체에 쉼표 있는 경우도 있기 때문)를 기준으로 더 세부적으로 뽑아내기
            tags_ext_lst = []#태그만 추출한 리스트(한 element에 한 데이터씩)
            
            for tags in filtered_dfs['UserChat']['tags'].tolist():
                if ', ' in tags:#', '로 나눠서 한 element에 하나의 태그만 들어가게
                    tag_split = tags.split(', ')
                    for tag in tag_split:
                        tags_ext_lst.append(tag.strip())
                else:
                    tags_ext_lst.append(tags)
            
            #한 번도 안 쓰인 태그 구하기
            tag_set = dfs['UserChatTag']['name'] # UserChatTags에 있는 것만 활용. 즉, UserChat에서'태그 없음(NaN)'은 데이터 분석에서 제외. '태그 없음' 포함하려면 tags_ext_lst을 set으로 감싸면 됨.
            tags_not_used = set([value for value in tag_set if value not in tags_ext_lst])
            
            #태그 종류별로 개수를 세기
            tag_types = []
            tag_count = []
            for tag in tag_set:
                tag_types.append(tag)
                tag_count.append(tags_ext_lst.count(tag))
            
            df_tags_count = pd.DataFrame({'문의 유형':tag_types, '건수':tag_count}).sort_values(by='건수', ascending=False)#건수 기준 내림차순 정렬
            
            if not show_all:
                #비율이 0.05가 안 되는 것들은 기타로 합치기
                #원본 데이터의 '기타'는 제외하고 나머지로 비율 계산
                ori_gita_count = int(df_tags_count.loc[df_tags_count['문의 유형'] == '기타']['건수'])#원본 기타 개수
                
                #원본 데이터의 '기타' 행은 빼기
                df_tags_count = df_tags_count[df_tags_count['문의 유형'] != '기타']
                
                tags_sum_count = df_tags_count['건수'].sum()
                tags_condition = (df_tags_count['건수']/tags_sum_count) > 0.05
                df_tags_count_without_gita = df_tags_count[tags_condition] #비율상 '기타로 빠지는 행들(원본 기타 건수는 이미 위에서 따로 저장해 놓음)'을 제외한 나머지 행들 저장
                df_tags_count_gita = df_tags_count[~tags_condition]
                
                #기타 행 추가(원본 기타 수 + 비율상 기타 수)
                sum_tags_gita = df_tags_count_gita['건수'].sum() + ori_gita_count
                df_tags_count = df_tags_count_with_gita = pd.concat([df_tags_count_without_gita, pd.DataFrame([['기타', sum_tags_gita]], columns=df_tags_count_without_gita.columns)], ignore_index=True)
                
            
            
            #문의 유형의 유형으로 다시 나누기
            #5개로 : [블랙보드], [도구], [오류], [출석], 기타
            #stacked bar chart
            st.write("##### 문의 유형의 종류")
            tag_class = ['블랙보드', '도구', '오류', '출석']
            tag_class_count = []
            
            tmp_df= df_tags_count.copy()#복사해 놓고 tag_class에 해당하는 거 추출해서 개수 센 다음 해당 행 삭제
            for tc in tag_class:
                df_ = df_tags_count[df_tags_count['문의 유형'].str.contains('\['+tc+'\]')]#df_로 개수 셈
                rm_idxes = df_.index#tmp_df에서 삭제할 인덱스
                tmp_df = tmp_df.drop(rm_idxes, axis=0)#삭제
                tag_class_count.append(df_['건수'].sum())#개수는 tag_class_count 리스트에 append
                
            #남은 건 기타로 append(show_all과 관계없이 원본이 기타인 것!)
            tag_class.append('기타')
            tag_class_count.append(tmp_df['건수'].sum())
            
            tmp_df = 0#메모리 절약 위해
            
            #비율 열 추가
            tag_class_count_ratio = []
            for count in tag_class_count:
                tag_class_count_ratio.append(count/sum(tag_class_count))
            
            df_tag_class_count = pd.DataFrame({'문의 유형':tag_class, '건수':tag_class_count, 'v':['문의 유형']*5, '비율':tag_class_count_ratio})
            df_tag_class_count = df_tag_class_count.sort_values(by='건수', ascending=False)
            df_tag_class_count = df_tag_class_count[df_tag_class_count['건수'] != 0]#개수 0인 행 제거
            #pd.DataFrame({'건수':'블랙보드':tag_class_count[0], '도구':tag_class_count[1], '오류':tag_class_count[2], '출석':tag_class_count[3], '기타':tag_class_count[4]}, columns=tag_class, index=[0])
            #print(df_tag_class_count)
            
            #altair stack bar chart
            c = alt.Chart(df_tag_class_count).mark_bar().encode(
                x=alt.X('sum(건수):Q', title=None).stack("normalize"),
                y=alt.Y('v', title=None).axis(labels=False),
                color=alt.Color('문의 유형', scale=alt.Scale(domain=df_tag_class_count['문의 유형'].tolist())), # 심볼을 수동으로 재정의하기: scale 객체를 사용하여 범례 심볼을 직접 지정. 여기선 dataframe의 column을 따르도록 함
                tooltip=['문의 유형', '건수', alt.Tooltip('비율', format='.1%')],
                order=alt.Order(
                  # Sort the segments of the bars by this field
                  'sum(건수):Q',
                  sort='descending'
                )
            )
            
            # 텍스트 레이블 정의 및 서식 지정
            text = alt.Chart(df_tag_class_count).mark_text(align='left', dy=-20, angle=330, color='black').encode(
                x=alt.X('sum(건수):Q', title=None).stack("normalize"),
                y=alt.Y('v', title=None).axis(labels=False),
                text=alt.Text('비율', format='.1%'),  # 레이블로 사용할 df의 열
                #color=alt.Color('문의 유형'),
                tooltip=['문의 유형', '건수', alt.Tooltip('비율', format='.1%')],
                order=alt.Order(
                  # Sort the segments of the bars by this field
                  'sum(건수):Q',
                  sort='descending'
                )
            )#.properties(selection=alt.selection_single())
            c = c+text
            c = c.configure_legend(#범례 설정
                orient='bottom', 
                direction='horizontal', 
                title=None
            )
            
            st.altair_chart(c, use_container_width=True)
            
            st.write("##### 태그별 건수")
            
            #데이터프레임 표로 보이기
            st.dataframe(df_tags_count, use_container_width = True, hide_index = True,
                         column_config={
                        "문의 유형": st.column_config.Column(
                            width = 'medium'
                        ),
                        "건수": st.column_config.Column(
                            width = 'small'
                        )
            })
            
     #%%       
    with col2:
        with st.container(border = True):
            st.write("### 사용자 통계")
            st.write("##### 사용자 유형별 이용 건수")
            #사용자 통계 보기 선택
            user_view_opt = st.selectbox(
                label = '',
                options = ('학적 상태로 보기', '과정 상태로 보기', '학년별 보기(기타 및 미식별 제외)'),
                label_visibility = "collapsed"#레이블 지우기(공간도 없앰); hidden은 공간은 남겨 놓음
                )
            
            if user_view_opt == '학적 상태로 보기':
                select_col = 'profile.user_role'
            elif user_view_opt == '과정 상태로 보기':
                select_col = 'profile.course_role'
            elif user_view_opt == '학년별 보기(기타 및 미식별 제외)':
                select_col = 'profile.education_level'
            
            #기간별 이용자를 user_role별로 분류하기
            
            #먼저 UserChat과 User 데이터 합치기(UserChat 중심)
            #suffixes는 열 이름 같은 경우 접미사 붙이기 기본값은 _x, _y
            df_Merged_UserChat_User= pd.merge(filtered_dfs['UserChat'], dfs['User'], left_on='userId', right_on='id', how='left', suffixes=('_Chat', '_User'))
            
            #NaN 처리
            if user_view_opt == '학년별 보기(기타 및 미식별 제외)':
                df_Merged_UserChat_User[select_col] = df_Merged_UserChat_User[select_col][df_Merged_UserChat_User[select_col] != '기타']
                df_Merged_UserChat_User = df_Merged_UserChat_User.dropna(subset=[select_col])
            else:
                df_Merged_UserChat_User[select_col] = df_Merged_UserChat_User[select_col].fillna('미식별(로그인 안 함)')#정확히 세기 위해서 결측치 nan을 실제 값으로 채워야 함.
    
            #user의 id가 없는 경우 로그인하지 않고 이용한 경우인 듯.
            #imsi = df_Merged_User_UserChat[df_Merged_User_UserChat['id'].isna()]#'id'가 NaN인 항목만 뽑아내기. personId는 있고, user의 id는 없는 경우
            #print(imsi)
            
            #user_role별 파이 차트를 위한 데이터 구축
            user_role_set = set(df_Merged_UserChat_User[select_col])
            user_role_lst = list(user_role_set)
            user_role_lst.sort()
            
            #색상 팔레트
            #role 범주별 색상 계열 위해(즉, 학부 재학, 학부 제적 등등끼리는 비슷한 색으로 표시하기 위해)
            #강사, 교원 : 파란색 계열
            #대학원 : 붉은색 개열
            #학부 : 초록색 계열
            #기타 : 회색 계열
            role_class = ('강사', '교원', '대학원', '학부')
            
            def code_sum(string):
                cs = 0
                for c in string:
                    cs += ord(c)
                return cs
            
            def dec_to_rgb(i):
                r = (int((255+i)/3)* (i+7)) % 255
                g = (int((255-i)*5) * (i+31)) % 255
                b = (int((255+i)/11) * (i+59)) % 255
                
                return abs(r), abs(g), abs(b)
                
            
            def to_color_code(r, g, b):
                return '#'+ f'{r:02x}' + f'{g:02x}' + f'{b:02x}'
            
            def set_palette(user_role_lst):#user_role에 대한 정보 바뀔 때마다 팔레트 다시 설정해야 함(예: 일부 정보 '기타'로 생략한 경우)
                palette = []
                for role in user_role_lst:
                    cs = code_sum(role)
                    r, g, b = dec_to_rgb(cs)
                    if re.match('강사|교원|교수자', role):# or re.match('교원', role) or re.match('교수자', role):
                        r = 44+int(r/2)
                        g = 44+int(g/1.7)
                        b = 255-int(b/6)
                    elif re.match('대학원|수업조교', role):# or re.match('수업조교', role):
                        r = 255-int(r/6)
                        g = 44+int(g/1.7)
                        b = 44+int(b/2)
                    elif re.match('학부|학습자|\d학년', role):# or re.match('학습자', role) or re.search('학년', role):
                        r = 44+int(r/1.7)
                        g = 255-int(g/6)
                        b = 44+int(b/2)
                    else:
                        r = 77+int(r/4)
                        g = 77+int(g/4)
                        b = 77+int(b/4)
                    palette.append(to_color_code(r, g, b))
                    
                return palette
            
            palette = set_palette(user_role_lst)
            
            #df_user_role_count = df_Merged_User_Message['profile.user_role'].value_counts().reset_index().rename(columns={'index':'User role', 'profile.user_role':'Counts'})
            
            df_user_role_count = df_Merged_UserChat_User[select_col].value_counts().reset_index().rename(columns={'index':'사용자 유형', select_col:'건수'})
            
            role_sum_count = df_user_role_count['건수'].sum()
            if not show_all:
                #비율이 0.05가 안 되는 것들은 기타로 합치기
                condition = (df_user_role_count['건수']/role_sum_count) > 0.05
                df_user_role_count_without_gita = df_user_role_count[condition] #일단 기타로 빠지는 행들을 제외한 나머지 행들 저장
                df_user_role_count_gita = df_user_role_count[~condition]
                
                #기타 행 추가
                if df_user_role_count_gita['건수'].sum() > 0:    
                    df_user_role_count_with_gita = pd.concat([df_user_role_count_without_gita, pd.DataFrame([['기타', df_user_role_count_gita['건수'].sum()]], columns=df_user_role_count_without_gita.columns)], ignore_index=True)
                else:
                    df_user_role_count_with_gita = df_user_role_count_without_gita
                
                df_user_role_count = df_user_role_count_with_gita
                
                #팔레트 업데이트
                palette = set_palette(sorted(list(set(df_user_role_count['사용자 유형']))))
            
            #altair radial chart
            #alt.Theta("values:Q").stack(True): Theta 축을 "values" 열로 지정하고, stack 파라미터를 True로 설정하여 데이터를 중첩시킵니다.
            #alt.Radius("values").scale(type="sqrt", zero=True, rangeMin=20): 반지름(Radius)을 "values" 열로 지정하고, 스케일링을 설정합니다. 여기서는 제곱근 스케일링을 사용하고, 최소값을 20으로 설정했습니다.
            
            #비율 열 추가
            user_role_count_ratio = []
            for count in df_user_role_count['건수']:
                user_role_count_ratio.append(count/df_user_role_count['건수'].sum())
            
            df_user_role_count['비율'] = user_role_count_ratio
            
            base = alt.Chart(df_user_role_count).encode(
                alt.Theta("건수:Q").stack(True),
                alt.Radius("건수").scale(type="sqrt", zero=True, rangeMin=20),
                color=alt.Color('사용자 유형:N', scale=alt.Scale(range=palette)),#, domain=df_user_role_count['사용자 유형'].tolist())),
                tooltip=['건수', '사용자 유형', alt.Tooltip('비율', format='.1%')],
                order=alt.Order(
                  # Sort the segments of the bars by this field
                  '건수:Q',
                  sort='descending'
                )
            )
            
            chart1 = base.mark_arc(innerRadius=20, stroke="#fff")
            
            chart2 = base.mark_text(radiusOffset=50).encode(text="사용자 유형:N",
                                                            color=alt.value('black'))
            chart4 = base.mark_text(radiusOffset=15).encode(text=alt.Text('비율', format='.1%'),
                                                            color=alt.value('black'))
            chart3 = chart1 + chart2 + chart4
            
            
            #c1, c2, c3 = st.columns([1, 6, 1])
            #with c2:
            st.altair_chart(chart3, use_container_width=True)
            
            def to_pydt(timestamp):
                return timestamp.to_pydatetime()
            def to_date(pydatetime):
                return pydatetime.date()
            
            
            #기간별 이용 추이 출력
            st.write("##### 기간별 이용 추이")
            df_period_usage = df_Merged_UserChat_User[['firstOpenedAt', select_col]]
            
            if not show_all:
                #5% 안 되는 거 기타로 뺴기(위에서 만든 거 활용)
                user_role_gita = set(df_user_role_count_gita['사용자 유형'])#기타에 해당하는 user_role 추출
                df_period_usage.loc[df_period_usage[select_col].isin(user_role_gita), select_col] = '기타'#기타에 해당하는 user_role 값들을 모두 '기타'로 바꾸기
                palette = set_palette(sorted(list(set(df_period_usage[select_col])))) #팔레트 업데이트
            #pd.timestamp를 pydatetime으로 바꾸기
            df_period_usage['firstOpenedAt'] = df_period_usage['firstOpenedAt'].apply(to_pydt).apply(to_date)
            #st.write(df_period_usage)
            
            #날짜별로 개수 세기
            #우선 role의 개수만큼 리스트 만들기(0으로 초기화)
            #date_user_role_count = dict()
            #for r in user_role_set:
            #    date_user_role_count[r] = []
            #
            #date_lst = []
            
            #날짜별, user_role별 개수 세기
            
            #for date in set(df_period_usage['firstOpenedAt']):
            #    date_lst.append(date)
            #    for role in user_role_set:
            #        cond = (df_period_usage['firstOpenedAt'] == date) & (df_period_usage[select_col] == role)
            #        date_user_role_count[role].append(len(df_period_usage[cond]))
                    
            #개수 센 걸로 데이터프레임 만들기
            #df_date = pd.DataFrame({'날짜':date_lst})
            #df_user_role_count = pd.DataFrame(date_user_role_count)
            #df_byPeriod_byRole_usage = pd.concat([df_date, df_user_role_count], axis=1)
            
            #df_byPeriod_byRole_usage = df_period_usage.groupby('firstOpenedAt', select_col).size().unstack().fillna(0)
            #groupby() 메서드는 데이터프레임을 특정 열(또는 열들)을 기준으로 그룹화하는 데 사용됩니다.
            #size() 메서드는 그룹화된 데이터프레임에서 각 그룹의 크기(행의 개수)를 반환합니다.
            #unstack() 메서드는 그룹화된 데이터프레임에서 특정 열을 행 인덱스로 변환하여 새로운 열을 생성합니다.
            
            #altair 차트 그릴 땐 이걸로
            df_byPeriod_byRole_usage = df_period_usage.groupby(['firstOpenedAt', select_col]).size().reset_index(name='Count')
            df_byPeriod_byRole_usage = df_byPeriod_byRole_usage.rename(columns={'firstOpenedAt':'날짜', select_col:'사용자 유형', 'Count':'건수'})
            
            
            #계열 열 추가하고 우선 '기타'로 초기화
            df_byPeriod_byRole_usage['계열'] = '기타'
            
            #각각 강사, 교원, 대학원, 학부에 해당하는 계열 값 설정
            #for rc in role_class:
            #    df_byPeriod_byRole_usage.loc[df_byPeriod_byRole_usage['사용자 유형'].str.contains(rc), '계열'] = rc
                #st.write(a)
            
            #st.write(df_byPeriod_byRole_usage)
            
            
            
            
            #st.write(user_role_lst)
            #st.write(palette)
            period_usage_chart = alt.Chart(df_byPeriod_byRole_usage).mark_bar().encode(
                x=alt.X('날짜', title=None),
                y=alt.X('건수:Q', title=None),
                color=alt.Color('사용자 유형:N', scale=alt.Scale(range=palette))#'사용자 유형:N'
            )
                
            st.altair_chart(period_usage_chart, use_container_width=True)
            
        #%%
    with col3:
        with st.container():
            st.write("### 일인당 상담 시간 평균")
            #상담 시간 평균 출력
            mean_time = filtered_dfs['UserChat']['operationTotalReplyTime'].mean()
            p_write(f"{mean_time.components.minutes}분 {mean_time.components.seconds}초", 80, "bold", "center")
            
            #절약 시간 출력
            total_time = filtered_dfs['UserChat']['operationTotalReplyTime'].sum()
            phone_time = filtered_dfs['UserChat'].shape[0] * pd.Timedelta(days=0, hours=0, minutes=15, seconds=0)
            saved_time = phone_time - total_time
            
            saved_str_font_size = 20
            saved_str1 = span_write("전화 상담 대비", font_size=saved_str_font_size, writeHTML=False)
            saved_str2 = span_write(f" 총 {saved_time.components.days * 24 + saved_time.components.hours}시간 {saved_time.components.minutes}분 {saved_time.components.seconds}초", font_size=saved_str_font_size, color=PRIMARY_COLOR, font_weight="bold", writeHTML=False)
            saved_str3 = span_write(" 절약", font_size=saved_str_font_size, writeHTML=False)
            saved_str4 = span_write("<br>(전화 상담 평균 15분 가정)", font_size=12, writeHTML=False)
            st.markdown(f'{saved_str1}{saved_str2}{saved_str3}{saved_str4}', unsafe_allow_html=True)
