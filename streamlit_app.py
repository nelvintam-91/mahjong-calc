import streamlit as st
import pandas as pd

# --- PAGE FUNCTIONS ---
def page_home():
    st.title("🀄 Mahjong Calculator")

    st.write("Active Players")
    with st.form("active_player_form"):
        st.multiselect("Select 4 players",
                       st.session_state['base_player_list_dedup'],
                       key="selected_players"
                      )
        confirm_button = st.form_submit_button(label='Confirm')
        if len(st.session_state['selected_players']) == 4 or confirm_button:
            var1, var2, var3, var4 = st.session_state['selected_players']    
            st.success(f'Active: {var1},{var2},{var3},{var4}')
        else:
            text_filler = 'Number of players incorrect'
            st.error(f':red[{text_filler}]')

    st.write("Add Game Results")
    with st.form("game_result_form"):
        col1, col2, col3, col4 = st.columns([1,1,1,1])

        with col1:
            winner = st.selectbox("Winner",
                        st.session_state['selected_players'],
                        index=None,
                        placeholder='Winner'
                        )

        with col2:
            loser = st.selectbox("Loser",
                        st.session_state['selected_players'],
                        index=None,
                        placeholder='Loser'
                        ) 

        with col3:
            win_type = st.selectbox("Type",
                        ['出銃','自摸','包自摸'],
                        index=None,
                        placeholder='Type'
                        )   

        with col4:
            points = st.selectbox("Points",
                        [3,4,5,6,7,8,9,10],
                        index=None,
                        placeholder='Points'
                        )    
    
        #Submit and delete last game buttons
        colA, colB = st.columns([3,1])
        with colB:
            OK_confirm_game_button = st.form_submit_button("OK")

        with colA:
            DEL_last_game_button = st.form_submit_button("Delete Last Game")

        if OK_confirm_game_button:
            if winner == loser:
                text_filler = 'Winner cannot have same name as Loser'
                st.error(f':red[{text_filler}]')
            elif win_type == None:
                text_filler = 'Win Type cannot be empty'
                st.error(f':red[{text_filler}]')
            elif points == None:
                text_filler = 'Points cannot be empty'
                st.error(f':red[{text_filler}]')
            elif loser == None and win_type != '自摸':
                text_filler = 'Loser cannot be nameless'
                st.error(f':red[{text_filler}]')
            elif win_type == '自摸':
                loser1 = [x for x in st.session_state['selected_players'] if x != winner][0]
                loser2 = [x for x in st.session_state['selected_players'] if x != winner][1]
                loser3 = [x for x in st.session_state['selected_players'] if x != winner][2]
                game_result = {'Winner': winner, 'Loser1': loser1, 'Loser2': loser2, 'Loser3': loser3, 'WinType': win_type, 'Points': points} 
                st.session_state['game_master'].append(game_result)
            else:
                loser1 = loser
                loser2 = None
                loser3 = None        
                game_result = {'Winner': winner, 'Loser1': loser1, 'Loser2': loser2, 'Loser3': loser3, 'WinType': win_type, 'Points': points} 
                st.session_state['game_master'].append(game_result)

        if DEL_last_game_button:
            mahjong_remove_last_line()


    #Calculation of winnings/losings
    mahjong_calculator()
    total_amount_df = pd.DataFrame(st.session_state['calculator_master'])
    if len(st.session_state['calculator_master']) > 0:
        total_amount = total_amount_df.groupby('Player').sum()        
        st.dataframe(total_amount.style.format({'Amount':'{:.2f}'}))

    game_master_df = pd.DataFrame(st.session_state['game_master'])
    st.write(game_master_df)

    with st.form("reset_form"):
        RESET_game_button = st.form_submit_button("DOUBLE CLICK TO RESET")
        if RESET_game_button:
            st.session_state['game_master'] = []
            st.session_state['calculator_master'] = []
            st.success('Game results have been reset.')

def page_player_settings():
    st.title("😁 Player Settings")

    st.write("Add/Remove Players")
    player_name_label = "Insert Player Name"
    with st.form("add_player_form"):
        col1, col2, col3 = st.columns([7,1,1])
               
        with col1:
            new_player_name = st.text_input(player_name_label,
                                            placeholder=player_name_label,
                                            label_visibility='collapsed')

        with col2:    
            ADD_button_player_name = st.form_submit_button("Add")

        with col3:
            RESET_button_player_name = st.form_submit_button("Reset")
        
        if ADD_button_player_name:
            new_player_name_cleansed = new_player_name.strip().upper()
            if 'base_player_list' not in st.session_state:
                st.session_state['base_player_list'] = ['NEL','WAI','CAM','BOS','LIL','LIS','AMA','JEN']
            st.session_state['base_player_list'].append(new_player_name_cleansed)

        if RESET_button_player_name:
            st.session_state['base_player_list'] = ['NEL','WAI','CAM','BOS','LIL','LIS','AMA','JEN']

    st.session_state['base_player_list_dedup'] = list(set(st.session_state['base_player_list']))
    st.session_state['base_player_list_dedup'].sort()
    st.session_state['player_df'] = pd.DataFrame(st.session_state['base_player_list_dedup'], columns=["Name"]) 
    st.dataframe(st.session_state['player_df'])    

def page_point_scoring():
    st.title("🎲 Points Scoring")
    
    with st.form("multiplier_form"):
        multiplier = st.selectbox(
                            "Multiplier",
                            [0.10,0.15,0.20],
                            index=None,
                            placeholder='Multiplier'
        )

        confirm_button_points = st.form_submit_button("OK")
        if confirm_button_points:
            st.session_state['multipler'] = multiplier
            st.success(f'Multipler set to {multiplier}')


    default_scoring = {
        "Points": [3,4,5,6,7,8,9,10],
        "SelfDraw": [4,8,12,16,24,32,48,64],
        "OutRight": [8,16,24,32,48,64,96,128]
    }

    default_scoring_df = pd.DataFrame(default_scoring)
    st.write(default_scoring_df)

def mahjong_calculator():
    st.session_state['calculator_master'] = []
    for x in range(len(st.session_state['game_master'])):
        winner_x = st.session_state['game_master'][x]['Winner']
        loser1_x = st.session_state['game_master'][x]['Loser1']
        loser2_x = st.session_state['game_master'][x]['Loser2']
        loser3_x = st.session_state['game_master'][x]['Loser3']
        win_type_x = st.session_state['game_master'][x]['WinType']
        points_x = st.session_state['game_master'][x]['Points']

        if win_type_x == '自摸':
            winner_x_entry = {'Player': winner_x, 'Amount': default_scoring_df.iloc[points_x-3]['SelfDraw']*st.session_state['multipler']*3.00}
            loser1_x_entry = {'Player': loser1_x, 'Amount': default_scoring_df.iloc[points_x-3]['SelfDraw']*st.session_state['multipler']*-1.00}
            loser2_x_entry = {'Player': loser2_x, 'Amount': default_scoring_df.iloc[points_x-3]['SelfDraw']*st.session_state['multipler']*-1.00}
            loser3_x_entry = {'Player': loser3_x, 'Amount': default_scoring_df.iloc[points_x-3]['SelfDraw']*st.session_state['multipler']*-1.00}
            st.session_state['calculator_master'].append(winner_x_entry)
            st.session_state['calculator_master'].append(loser1_x_entry)
            st.session_state['calculator_master'].append(loser2_x_entry)
            st.session_state['calculator_master'].append(loser3_x_entry)
        elif win_type_x == '包自摸':
            winner_x_entry = {'Player': winner_x, 'Amount': default_scoring_df.iloc[points_x-3]['SelfDraw']*st.session_state['multipler']*3.00}
            loser1_x_entry = {'Player': loser1_x, 'Amount': default_scoring_df.iloc[points_x-3]['SelfDraw']*st.session_state['multipler']*-3.00}
            st.session_state['calculator_master'].append(winner_x_entry)
            st.session_state['calculator_master'].append(loser1_x_entry)
        else:
            winner_x_entry = {'Player': winner_x, 'Amount': default_scoring_df.iloc[points_x-3]['OutRight']*st.session_state['multipler']*1.00}
            loser1_x_entry = {'Player': loser1_x, 'Amount': default_scoring_df.iloc[points_x-3]['OutRight']*st.session_state['multipler']*-1.00}
            st.session_state['calculator_master'].append(winner_x_entry)
            st.session_state['calculator_master'].append(loser1_x_entry)

def mahjong_remove_last_line():
    del st.session_state['game_master'][-1]


# --- MAIN APP ---
def main():
    st.sidebar.title("Nav")
    selection = st.sidebar.radio(
        "Go to",
        ["Home","Players","Points"]
    )

    if selection == "Home":
        page_home()
    elif selection == "Players":
        page_player_settings()
    elif selection == "Points":
        page_point_scoring()

    st.sidebar.markdown("---")
    st.sidebar.caption("v1.0.0 | Nelvin Tam")

    

if __name__ == "__main__":
    #Set up session state tables
    if 'base_player_list_dedup' not in st.session_state:
        st.session_state['base_player_list_dedup'] = ['NEL','WAI','CAM','BOS','LIL','LIS','AMA','JEN']
    st.session_state['base_player_list_dedup'].sort()
    if 'base_player_list' not in st.session_state:
        st.session_state['base_player_list'] = st.session_state['base_player_list_dedup'] 
    if 'game_master' not in st.session_state:
        st.session_state['game_master'] = []  
    if 'multipler' not in st.session_state:
        st.session_state['multipler'] = 0.15
    if 'calculator_master' not in st.session_state:
        st.session_state['calculator_master'] = []  



    #Default scoring system
    default_scoring = {
        "Points": [3,4,5,6,7,8,9,10],
        "SelfDraw": [4,8,12,16,24,32,48,64],
        "OutRight": [8,16,24,32,48,64,96,128]
    }
    default_scoring_df = pd.DataFrame(default_scoring)

    main()