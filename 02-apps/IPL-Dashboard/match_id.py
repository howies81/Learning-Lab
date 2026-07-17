
"""
Cricsheet IPL 2026 Data Loader
===============================
Loads IPL 2026 season data from a full Cricsheet IPL archive folder
and produces 4 clean dataframes/CSV files:
 
    players.csv    — one row per player (name + Cricsheet ID)
    matches.csv    — one row per match (venue, teams, result etc.)
    deliveries.csv — one row per ball bowled
    officials.csv - one row per official
 
Only matches with ID >= 1527674 are loaded (start of 2026 IPL season).
 
Usage:
    1. Set DATA_FOLDER to the path of your folder
    2. Run: python cricket_loader.py
"""

import pandas as pd
import os
import json 
import numpy as np 

IPL_DATA_FOLDER = "./ipl_male_json"
FIRST_2026_REG_SEASON_MATCH = 1527674
LAST_2026_REG_SEASON_MATCH = 1529313
FINAL_MATCH = 1535465


def get_2026_match_IDs(folder_path):
    """
    Scans the folder for all delivery CSVs and returns only
    match IDs >= FIRST_2026_MATCH.
    """
    all_ids = []
    all_reg_season_ids = []
    all_playoff_ids = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            try:
                match_id = int(filename.replace(".json", ""))
                if match_id >= FIRST_2026_REG_SEASON_MATCH:
                    all_ids.append(match_id)
            except ValueError:
                pass  # skip any files that don't have a numeric name
 
    all_ids.sort()
    all_playoff_ids = all_ids[-4:]
    all_reg_season_ids = all_ids[:-4]
    return all_ids, all_reg_season_ids, all_playoff_ids


match_ids, reg_season_ids, playoff_ids = get_2026_match_IDs(IPL_DATA_FOLDER)
#print(match_ids)

#print(reg_season_ids)

# print(playoff_ids)

# # ### Get 2026 Match Reg Season Info


# -------------------------------------------------------
# STEP 2: Get match and player info for reg season
# -------------------------------------------------------
def load_match_info(folder, match_ids):
    """
    Reads .json for each 2026 match and returns:
      - matches_df : one row per match
      - players_df : unique player registry (name + Cricsheet ID)
      - officials_df: unique official registry
    """
    all_matches = []
    all_registry = []
    all_players = []
    all_officials = []
 
    for match_id in match_ids:
        filename = f"{match_id}.json"
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            print(f"  Warning: {filename} not found, skipping")
            continue
 
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                d = json.load(f)
 
            # --- Get registry info ------
            registry_people = d.get("info", {}).get("registry", {}).get("people",{})
 
            # --- Retrieve data for names and Cricsheet ID ---
            for player_name, cricsheet_id in registry_people.items():
                if player_name and cricsheet_id:
                    all_registry.append({
                        "player_name": player_name,
                        "id": cricsheet_id
                    })


            # ---Get player info ----
            player_data = d.get("info", {}).get("players", {})
            for team, player_list in player_data.items():
                if team and player_list:
                    for player in player_list:
                        all_players.append({
                            "player_name": player,
                            "team": team
                        })

            # --- Get match info ----
            match_data = d.get("info", {})
            match_city = match_data.get("city", "")
            match_dates = match_data.get("dates", [])
            match_date = match_dates[0] if match_dates else ""
            match_number = match_data.get("event", {}).get("match_number", str(0))

            outcome_data = match_data.get("outcome", {})
            match_winner = ""
            match_outcome = ""
            
            if "winner" in outcome_data:
                match_winner = outcome_data.get("winner", "")
                match_outcome = outcome_data.get("by", {})
                if "wickets" in match_outcome:
                    match_outcome_w_r = "wickets"
                    match_outcome_amt = match_outcome.get("wickets", str(0))
                elif "runs" in match_outcome:
                    match_outcome_w_r = "runs"
                    match_outcome_amt = match_outcome.get("runs", str(0))
            elif "eliminator" in outcome_data:
                match_winner = outcome_data.get("eliminator", "")
                match_outcome = outcome_data.get("result", "")
                match_outcome_w_r = ""
                match_outcome_amt = ""
            elif "result" in outcome_data:
                match_winner = "NR"
                match_outcome = outcome_data.get("result", "")
                match_outcome_w_r = ""
                match_outcome_amt = ""


            # --- Teams Logic ---
            teams = match_data.get("teams", [])
            team_1 = teams[0] if len(teams) > 0 else ""
            team_2 = teams[1] if len(teams) > 1 else ""

            match_toss_winner = match_data.get("toss", {}).get("winner", "")
            match_toss_decision = match_data.get("toss", {}).get("decision", "")
            match_venue = match_data.get("venue", "")

            all_matches.append({
                "match_id": match_id,
                "city": match_city,
                "date": match_date,
                "number": match_number,
                "winner": match_winner,
                "outcome": match_outcome,
                "wickets_runs": match_outcome_w_r,
                "winning_amount": match_outcome_amt,
                "toss_winner": match_toss_winner,
                "toss_decision": match_toss_decision,
                "venue": match_venue,
                "team1": team_1,
                "team2": team_2

            })
            
            #Get official info
            official_data = match_data.get("officials", {})
            match_referees = official_data.get("match_referees", [])
            match_referee = match_referees[0] if match_referees else ""
            reserve_umpires = official_data.get("reserve_umpires", [])
            reserve_umpire = reserve_umpires[0] if reserve_umpires else ""
            tv_umpires = official_data.get("tv_umpires", [])
            tv_umpire = tv_umpires[0] if tv_umpires else ""
            umpires = official_data.get("umpires", [])
            if umpires:
                umpire1 = umpires[0] 
                umpire2 = umpires[1]
                
            else:
                umpire1 = ""
                umpire2 = ""

            all_officials.append({
                "match_id": match_id,
                "match_referee": match_referee,
                "reserve_umpire": reserve_umpire,
                "tv_umpire": tv_umpire,
                "first_umpire": umpire1,
                "second_umpire": umpire2
            })
        
        except Exception as e:
            print(f"  Warning: could not load {filename} — {e}")
 
    matches_df = (pd.DataFrame(all_matches))
    #print(matches_df)
    officials_df = (pd.DataFrame(all_officials))
    registry_df = (pd.DataFrame(all_registry).drop_duplicates(subset="player_name"))
    #print(registry_df)                
    players_df = (pd.DataFrame(all_players).drop_duplicates(subset="player_name"))
    #print(team_df)
    players_id_df = (pd.merge(registry_df, players_df, on="player_name", how='left').sort_values("team").reset_index(drop=True))
 
    # print(f"✓ Matches loaded:  {len(matches_df)}")
    # print(f"✓ Players found:   {len(players_df)}")
    return matches_df, players_id_df, registry_df

#------------------------------------------------------------------------------------------

def load_delivery_files(folder, match_ids):
    """
    Reads the ball-by-ball delivery CSV for each 2026 match.
    
    """
    all_deliveries = []
 
    #print(f"\nLoading delivery files...")
 
    for match_id in match_ids:
        filename = f"{match_id}.json"
        filepath = os.path.join(folder, filename)
 
        if not os.path.exists(filepath):
            print(f"  Warning: {filename} not found, skipping")
            continue
 
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                d = json.load(f)

            innings_data = d.get("innings", [])
            for innings in innings_data[:2]:
                team = innings.get("team", "")

                powerplays_data = innings.get("powerplays", [])
                powerplays_from = 0.0
                powerplays_to = 0.0
                powerplays_type = ""
                if powerplays_data:
                    powerplays_from = powerplays_data[0].get("from", 0.0)
                    powerplays_to = powerplays_data[0].get("to", 0.0)
                    powerplays_type = powerplays_data[0].get("type", "")

                for overs_data in innings.get("overs", []):
                    over = overs_data.get("over", -1)

                    for delivery in overs_data.get("deliveries", []):
                        actual_delivery = delivery.get("actual_delivery", "")
                        batsman = delivery.get("batter", "")
                        bowler = delivery.get("bowler", "")
                        extra_data = delivery.get("extras", {})
                        extra_type = ""
                        extra_value = 0
                        if extra_data:
                            for extra, value in extra_data.items():
                                extra_type = extra
                                
                        non_striker = delivery.get("non_striker", "")
                        batter_runs = delivery.get("runs", {}).get("batter", "")
                        extra_runs = delivery.get("runs", {}).get("extras", "")
                        total_runs = delivery.get("runs", {}).get("total", "")
                        review_by = delivery.get("review", {}).get("by", "")
                        review_umpire = delivery.get("review", {}).get("umpire", "")
                        review_batter = delivery.get("review", {}).get("batter", "")
                        review_decision = delivery.get("review", {}).get("decision", "")
                        review_type = delivery.get("review", {}).get("type", "")
                        wickets_data_list = delivery.get("wickets", [])
                        player_out = ""
                        wicket_fielder = []
                        wicket_fielder_name = ""
                        wicket_kind = ""
                        if wickets_data_list:
                            player_out = wickets_data_list[0].get("player_out", "")
                            wicket_fielder = wickets_data_list[0].get("fielders", [])
                            if wicket_fielder:
                                wicket_fielder_name = wicket_fielder[0].get("name", "")
                            wicket_kind = wickets_data_list[0].get("kind", "")
                        if (float(actual_delivery) >= powerplays_from) and (float(actual_delivery) <= powerplays_to):                       
                            powerplay_flag = 1
                            current_powerplay_type = powerplays_type
                        else:
                            powerplay_flag = 0
                            current_powerplay_type = ""
                        


                        all_deliveries.append({
                            "match_id":match_id,
                            "team": team,
                            "over": over,
                            "actual_delivery": actual_delivery,
                            "batsman": batsman,
                            "bowler": bowler,
                            "non_striker": non_striker,
                            "batter_runs": batter_runs,
                            "extra_type": extra_type,
                            "extra_runs": extra_runs,
                            "total_runs": total_runs,
                            "review_by": review_by,
                            "review_umpire": review_umpire,
                            "review_batter": review_batter,
                            "review_decision": review_decision,
                            "review_type": review_type,
                            "player_out": player_out,
                            "wicket_fielder": wicket_fielder_name,
                            "wicket_kind": wicket_kind,
                            "powerplay_flag": powerplay_flag,
                            "powerplays_type": current_powerplay_type
                                })
 
        except Exception as e:
            print(f"  Warning: could not load {filename} — {e}")
 
    deliveries_df = pd.DataFrame(all_deliveries)
    print(f"✓ Total deliveries loaded: {len(deliveries_df):,}")
    return deliveries_df

#print(len(match_ids))

# Regular season Match IDs, Player Lineups, Official Lineups and Delivery Logs
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
matches_df, players_df, registry_df= load_match_info(IPL_DATA_FOLDER, reg_season_ids)
# print(matches_df)
# print("\n")

officials_df = players_df[players_df['team'].isna()].reset_index()
# print(officials_df)
# print("\n")
players_df = players_df[(players_df['team']).notna()]
# print(players_df)
# print("\n")

deliveries_df = load_delivery_files(IPL_DATA_FOLDER, reg_season_ids)
# print(deliveries_df.info())

# Playoff Match IDs, Player Lineups, Official Lineups and Delivery Logs
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
playoff_matches_df, playoff_players_df, playoff_registry_df= load_match_info(IPL_DATA_FOLDER, playoff_ids)
# print(playoff_matches_df)
# print("\n")

playoff_officials_df = playoff_players_df[playoff_players_df['team'].isna()].reset_index()
# print(playoff_officials_df)
# print("\n")
playoff_players_df = playoff_players_df[(playoff_players_df['team']).notna()]
# print(playoff_players_df)
# print("\n")

playoff_deliveries_df = load_delivery_files(IPL_DATA_FOLDER, playoff_ids)
# print(playoff_deliveries_df.info())

# Whole Season Match IDs, Player Lineups, Official Lineups and Delivery Logs
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
whole_matches_df, whole_players_df, whole_registry_df= load_match_info(IPL_DATA_FOLDER, match_ids)
# print(whole_matches_df)
# print("\n")

whole_officials_df = whole_players_df[whole_players_df['team'].isna()].reset_index()
# print(whole_officials_df)
# print("\n")
whole_players_df = whole_players_df[(whole_players_df['team']).notna()]
# print(whole_players_df)
# print("\n")

whole_deliveries_df = load_delivery_files(IPL_DATA_FOLDER, match_ids)
# print(whole_deliveries_df.info())


#----------------------------------------------------------------------------------------

def calculate_batting_stats(deliveries_df, players_df):
     """
    Calculates overall season batting stats for every player from the deliveries DataFrame.
    Returns a single player_stats_df with one row per player containing:
      - Batting stats
    All joined to the players table on player_name.

    Corrections applied:
      - Wides excluded from balls faced (no-balls count as faced)
      - Dismissals counted via player_dismissed (catches non-striker run outs too)
    """
     
      # -------------------------------------------------------
    # BATTING STATS
    # grouped by striker (the batter facing the ball)
    # -------------------------------------------------------

    # A ball counts as faced only if it's not a wide
    # No-balls count as faced — batter can play the ball
     deliveries_df["ball_faced"] = ((deliveries_df["extra_type"] != "wides") & (deliveries_df["extra_type"] != "noballs")).astype(int)

    # Boundary fours and sixes
     deliveries_df["is_four"] = (deliveries_df["batter_runs"] == 4).astype(int)
     deliveries_df["is_six"]  = (deliveries_df["batter_runs"] == 6).astype(int)

     #Dot balls
     deliveries_df["is_dot_ball"] = (deliveries_df["total_runs"] == 0).astype(int)

     #Separate deliveries of innings into Powerplay, Middle Period and Death Overs
     

    # Assign clean flags that completely ignore individual wide/no-ball row counts
     deliveries_df["is_death"] = (
    (deliveries_df["over"] >= 15) & 
    (deliveries_df["powerplay_flag"] == 0)
     ).astype(int)

     deliveries_df["is_middle"] = (
    (deliveries_df["powerplay_flag"] == 0) & 
    (deliveries_df["is_death"] == 0)
     ).astype(int)

         

     ## ----------------------------------------------------
     ## POWERPLAY BATTING STATS
     ## ----------------------------------------------------
     pp_batting_stats = deliveries_df[deliveries_df["powerplay_flag"] == 1].groupby("batsman").agg(
          pp_runs      = ("batter_runs",     "sum"),
          pp_balls_faced = ("ball_faced",    "sum"),
          pp_dot_balls   = ("is_dot_ball",   "sum"),
          pp_fours       = ("is_four",       "sum"),
          pp_sixes       = ("is_six",        "sum"),
          pp_innings_batted = ("match_id",    "nunique")
     ).reset_index().rename(columns= {"batsman": "player_name"})

     ## ----------------------------------------------------
     ## MIDDLE OVERS BATTING STATS
     ## ----------------------------------------------------
     middle_batting_stats = deliveries_df[deliveries_df["is_middle"] == 1].groupby("batsman").agg(
          middle_runs          = ("batter_runs",     "sum"),
          middle_balls_faced   = ("ball_faced",      "sum"),
          middle_dot_balls     = ("is_dot_ball",     "sum"),
          middle_fours         = ("is_four",         "sum"),
          middle_sixes         = ("is_six",          "sum"),
          middle_innings_batted = ("match_id",       "nunique")
     ).reset_index().rename(columns={"batsman": "player_name"})
     
     ## ----------------------------------------------------
     ## DEATH OVERS BATTING STATS
     ## ----------------------------------------------------
     death_batting_stats = deliveries_df[deliveries_df["is_death"] == 1].groupby("batsman").agg(
          death_runs          = ("batter_runs",     "sum"),
          death_balls_faced   = ("ball_faced",      "sum"),
          death_dot_balls     = ("is_dot_ball",     "sum"),
          death_fours         = ("is_four",         "sum"),
          death_sixes         = ("is_six",          "sum"),
          death_innings_batted = ("match_id",       "nunique")
     ).reset_index().rename(columns={"batsman": "player_name"})

     ## -----------------------------------------------------
     ## INNINGS PERIOD BATTING STATS
     ## -----------------------------------------------------
     master_batting_df = pp_batting_stats.merge(middle_batting_stats, on="player_name", how="outer")
     master_batting_df = master_batting_df.merge(death_batting_stats, on="player_name", how="outer")
     master_batting_df.fillna(0, inplace=True)

     ## STRIKE RATE FOR EACH BATSMAN FOR EACH PHASE
     master_batting_df["pp_strike_rate"] = (master_batting_df["pp_runs"] / master_batting_df["pp_balls_faced"] * 100).fillna(0).round(2)
     master_batting_df["middle_strike_rate"] = (master_batting_df["middle_runs"] / master_batting_df["middle_balls_faced"] * 100).fillna(0).round(2)
     master_batting_df["death_strike_rate"] = (master_batting_df["death_runs"] / master_batting_df["death_balls_faced"] * 100).fillna(0).round(2)

     ## BATTING BOUNDARY PERCENTAGE FOR EACH BATSMAN EACH PHASE
     master_batting_df["pp_boundary_pct"] = ((master_batting_df["pp_fours"] + master_batting_df["pp_sixes"]) / master_batting_df["pp_balls_faced"] * 100).fillna(0).round(2)
     master_batting_df["middle_boundary_pct"] = ((master_batting_df["middle_fours"] + master_batting_df["middle_sixes"]) / master_batting_df["middle_balls_faced"] * 100).fillna(0).round(2)
     master_batting_df["death_boundary_pct"] = ((master_batting_df["death_fours"] + master_batting_df["death_sixes"]) / master_batting_df["death_balls_faced"] * 100).fillna(0).round(2)

     ## DOT BALL PERCENTAGE FOR EACH BATSMAN FOR EACH PHASE
     master_batting_df["pp_dot_ball_pct"] = (master_batting_df["pp_dot_balls"] / master_batting_df['pp_balls_faced'] *100).fillna(0).round(2)
     master_batting_df["middle_dot_ball_pct"] = (master_batting_df["middle_dot_balls"] / master_batting_df['middle_balls_faced'] *100).fillna(0).round(2)
     master_batting_df["death_dot_ball_pct"] = (master_batting_df["death_dot_balls"] / master_batting_df['death_balls_faced'] *100).fillna(0).round(2)

     
     #Non boundary Strike Rate - PowerPlay
     master_batting_df["pp_non_boundary_runs"] = (master_batting_df["pp_runs"] - ((4 * master_batting_df["pp_fours"]) + (6 * master_batting_df["pp_sixes"]))).fillna(0)
     master_batting_df["pp_non_boundary_balls"] =(master_batting_df["pp_balls_faced"] -(master_batting_df["pp_fours"] + master_batting_df["pp_sixes"])).fillna(0)
     master_batting_df["pp_non_boundary_strike_rate"] = (master_batting_df["pp_non_boundary_runs"] / master_batting_df["pp_non_boundary_balls"] * 100).fillna(0).round(2)

     #Non boundary Strike Rate - Middle Overs
     master_batting_df["middle_non_boundary_runs"] = (master_batting_df["middle_runs"] - ((4 * master_batting_df["middle_fours"]) + (6 * master_batting_df["middle_sixes"]))).fillna(0)
     master_batting_df["middle_non_boundary_balls"] =(master_batting_df["middle_balls_faced"] -(master_batting_df["middle_fours"] + master_batting_df["middle_sixes"])).fillna(0)
     master_batting_df["middle_non_boundary_strike_rate"] = (master_batting_df["middle_non_boundary_runs"] / master_batting_df["middle_non_boundary_balls"] *100).fillna(0).round(2)

     #Non boundary Strike Rate - Death Overs
     master_batting_df["death_non_boundary_runs"] = (master_batting_df["death_runs"] - ((4 * master_batting_df["death_fours"]) + (6 * master_batting_df["death_sixes"]))).fillna(0)
     master_batting_df["death_non_boundary_balls"] =(master_batting_df["death_balls_faced"] -(master_batting_df["death_fours"] + master_batting_df["death_sixes"])).fillna(0)
     master_batting_df["death_non_boundary_strike_rate"] = (master_batting_df["death_non_boundary_runs"] / master_batting_df["death_non_boundary_balls"] * 100).fillna(0).round(2)

     ## --------------------------------------------------
     ## OVERALL BATTING STATS
     ## ----------------------------------------------------
     batting_stats = deliveries_df.groupby("batsman").agg(
        runs           = ("batter_runs",  "sum"),
        balls_faced    = ("ball_faced",    "sum"),
        dot_balls      = ("is_dot_ball",   "sum"),
        fours          = ("is_four",       "sum"),
        sixes          = ("is_six",        "sum"),
        innings_batted = ("match_id",      "nunique")
    ).reset_index().rename(columns={"batsman": "player_name"})
     
     # Dismissals — grouped by player_dismissed so non-striker run outs are included
     dismissals = (deliveries_df[(deliveries_df["player_out"].notna()) & (deliveries_df["player_out"] != "")]
                    .groupby("player_out")
                    .size()
                    .reset_index())
     dismissals.columns = ["player_name", "dismissals"]

     batsman_scores = deliveries_df.groupby(["batsman", "match_id"])["batter_runs"].sum().reset_index()
     batsman_scores["fifties"] = np.where((batsman_scores["batter_runs"] >= 50) & (batsman_scores["batter_runs"] < 100), 1, 0)
     batsman_scores["hundreds"] = np.where((batsman_scores["batter_runs"] >= 100), 1, 0)
     batsman_milestones = batsman_scores.groupby("batsman").agg(
        highest_score          =("batter_runs",    "max"),
        fifties                =("fifties",        "sum"),
        hundreds               =("hundreds",       "sum")
     ).reset_index().rename(columns={"batsman": "player_name"})

     batting_stats = batting_stats.merge(dismissals, on="player_name", how="left")
     batting_stats["dismissals"] = batting_stats["dismissals"].fillna(0).astype(int)

     batting_stats = batting_stats.merge(batsman_milestones, on="player_name", how="outer")

    # Strike rate = (runs / balls faced) * 100
     batting_stats["strike_rate"] = (
        batting_stats["runs"] / batting_stats["balls_faced"] * 100
    ).round(2)

    # Batting average = runs / dismissals (NaN if never dismissed)
     batting_stats["batting_average"] = (
        batting_stats["runs"] / batting_stats["dismissals"].replace(0, float("nan"))
    ).round(2)
     
    # Batting boundary percentage = (fours + sixes) / balls_faced * 100
     batting_stats["boundary_pct"] = ((batting_stats["fours"] + batting_stats["sixes"]) / batting_stats["balls_faced"] * 100).round(2)
     
     # Dot ball percentage
     batting_stats["dot_ball_pct"] = (batting_stats["dot_balls"] / batting_stats['balls_faced'] * 100).round(2)

     #Non boundary Strike Rate
     batting_stats["non_boundary_runs"] = (batting_stats["runs"] - ((4 * batting_stats["fours"]) + (6 * batting_stats["sixes"])))
     batting_stats["non_boundary_balls"] =(batting_stats["balls_faced"] -(batting_stats["fours"] + batting_stats["sixes"]))
     batting_stats["non_boundary_strike_rate"] = (batting_stats["non_boundary_runs"] / batting_stats["non_boundary_balls"] * 100).round(2)

     
     player_batting_stats_df = (players_df
        .merge(batting_stats,  on="player_name", how="left"))
     player_batting_stats_df = (player_batting_stats_df.merge(master_batting_df, on="player_name", how="outer"))
     
     print(f"✓ Player stats calculated: {len(player_batting_stats_df)} players")
    #  print(f"  Columns: {list(player_batting_stats_df.columns)}")

     return player_batting_stats_df

#Batting stats for regular season
player_batting_stats_df = calculate_batting_stats(deliveries_df=deliveries_df, players_df=players_df)
player_batting_stats_df= player_batting_stats_df[(player_batting_stats_df["team"].notna())]
print("\n")
# print(player_batting_stats_df)

#Batting stats for playoff season
# playoff_player_batting_stats_df = calculate_batting_stats(deliveries_df=playoff_deliveries_df, players_df=playoff_players_df)
# playoff_player_batting_stats_df= playoff_player_batting_stats_df[(playoff_player_batting_stats_df["team"].notna())]
# print("\n")
# print(playoff_player_batting_stats_df)

#Batting stats for whole season
# whole_player_batting_stats_df = calculate_batting_stats(deliveries_df=whole_deliveries_df, players_df=whole_players_df)
# whole_player_batting_stats_df= whole_player_batting_stats_df[(whole_player_batting_stats_df["team"].notna())]
# print("\n")
# print(whole_player_batting_stats_df)



# print(whole_player_batting_stats_df[whole_player_batting_stats_df["player_name"].str.contains("Suryavanshi")])

# print("\n")
# print(whole_player_batting_stats_df[whole_player_batting_stats_df["player_name"].str.contains("Kohli")])

# print(player_batting_stats_df[player_batting_stats_df["player_name"].str.contains("Suryavanshi")])

# print("\n")
# print(player_batting_stats_df[player_batting_stats_df["player_name"].str.contains("Kohli")])

# deliveries_df["wicket_kind"].unique()

# -------------------------------------------------------------------------------------------

def calculate_bowling_stats(deliveries_df, players_df):
    """
    Calculates overall season bowling stats for every player from the deliveries DataFrame.
    Returns a single player_stats_df with one row per player containing:
      - Bowling stats
    All joined to the players table on player_name.

    Corrections applied:
      - Runs conceded includes wides and no-balls (but not byes or leg byes)
    """

    # -------------------------------------------------------
    # BOWLING STATS
    # grouped by bowler
    # -------------------------------------------------------

    # A legal delivery excludes wides and no-balls
    deliveries_df["is_legal"] = (
        (deliveries_df["extra_type"] != "wides") & (deliveries_df["extra_type"] != "noballs")
    ).astype(int)

    deliveries_df["wides"] = np.where(deliveries_df["extra_type"] == "wides", deliveries_df["extra_runs"], 0)
    deliveries_df["noballs"] = np.where(deliveries_df["extra_type"] == "noballs", deliveries_df["extra_runs"], 0)

    # Runs conceded by bowler = runs off bat + wides + no-balls
    # Byes and leg byes are NOT the bowler's fault
    deliveries_df["runs_conceded"] = (
        deliveries_df["batter_runs"].fillna(0) +
        deliveries_df["wides"].fillna(0) +
        deliveries_df["noballs"].fillna(0)
    )

     # Wickets credited to bowler — excludes run outs, retired hurt, obstructions
    deliveries_df["bowler_wicket"] = (
        deliveries_df["wicket_kind"].notna() &
        ~deliveries_df["wicket_kind"].isin([
            "run out", "retired hurt", "retired out", "obstructing the field", ""
        ])
    ).astype(int)

    # Dot balls = legal delivery where total runs == 0
    deliveries_df["is_dot"] = (
        (deliveries_df["is_legal"] == 1) & (deliveries_df["total_runs"] == 0)
    ).astype(int)

    # Boundaries balls = delivery where runs off bat == 4 OR 6
    deliveries_df["is_boundary"] = (
        (deliveries_df["batter_runs"].isin([4, 6]))
    ).astype(int)

    bowling_stats = deliveries_df.groupby("bowler").agg(
        balls_bowled   = ("is_legal",        "sum"),
        runs_conceded  = ("runs_conceded",    "sum"),
        wickets        = ("bowler_wicket",    "sum"),
        dot_balls      = ("is_dot",           "sum"),
        boundaries     = ("is_boundary",      "sum"),
        innings_bowled = ("match_id",         "nunique")
    ).reset_index().rename(columns={"bowler": "player_name"})

    # Overs bowled (balls / 6, rounded to 1 decimal)
    bowling_stats["over"], bowling_stats["ball"] = bowling_stats["balls_bowled"].divmod(6)
    bowling_stats["overs_bowled"] = (bowling_stats["over"].astype(int).astype(str) + '.' + bowling_stats["ball"].astype(int).astype(str)).astype(float)

    bowling_figures = deliveries_df.groupby(["bowler", "match_id"]).agg(
        match_wickets   =("bowler_wicket",      "sum"),
        match_runs      =("runs_conceded",      "sum"),
        match_balls     =("is_legal",           "sum"),
        match_dot_balls =("is_dot",             "sum")
    ).reset_index().sort_values(
        by= ["match_wickets", "match_runs", "match_balls", "match_dot_balls"],
        ascending= [False, True, True, False]
    ).rename(columns={"bowler": "player_name"})

    # Overs bowled (balls / 6, rounded to 1 decimal)
    bowling_figures["best_figures"] = (
        bowling_figures["match_wickets"].astype(int).astype(str) + "/" + bowling_figures["match_runs"].astype(int).astype(str)
    )

    bowling_figures = bowling_figures.drop_duplicates(
        subset=["player_name"],
        keep="first"
    )

    bowling_figures = bowling_figures.drop(columns=["match_id", "match_wickets", "match_runs", "match_balls", "match_dot_balls"])

    bowling_stats = bowling_stats.merge(bowling_figures, on="player_name", how="outer")

    

    # Economy rate = runs conceded per over
    bowling_stats["economy"] = (
        bowling_stats["runs_conceded"] / bowling_stats["balls_bowled"] * 6
    ).round(2)

    # Bowling average = runs conceded per wicket
    bowling_stats["bowling_average"] = (
        bowling_stats["runs_conceded"] / bowling_stats["wickets"].replace(0, float("nan"))
    ).round(2)

    # Bowling strike rate = balls bowled per wicket
    bowling_stats["bowling_strike_rate"] = (
    bowling_stats["balls_bowled"] / bowling_stats["wickets"].replace(0, float("nan"))
    ).round(2)

    # Boundary percentage = legal deliveries hit for 4 or 6
    bowling_stats["boundary_pct"] = (bowling_stats["boundaries"] / bowling_stats["balls_bowled"] * 100).round(2)

    # Balls per boundary  = (Boundary percentage/100)^(-1)
    bowling_stats["balls_per_boundary"] = (100 / bowling_stats["boundary_pct"]).astype(int)    

    #Separate deliveries of innings into Powerplay, Middle Period and Death Overs
    # Assign clean flags that completely ignore individual wide/no-ball row counts
    deliveries_df["is_death"] = (
    (deliveries_df["over"] >= 15) & 
    (deliveries_df["powerplay_flag"] == 0)
     ).astype(int)

    deliveries_df["is_middle"] = (
    (deliveries_df["powerplay_flag"] == 0) & 
    (deliveries_df["is_death"] == 0)
     ).astype(int)


    ## ----------------------------------------------------
    ## POWERPLAY BOWLING STATS
    ## ----------------------------------------------------
    pp_bowling_stats = deliveries_df[deliveries_df["powerplay_flag"] == 1].groupby("bowler").agg(
        pp_balls_bowled   = ("is_legal",        "sum"),
        pp_runs_conceded  = ("runs_conceded",    "sum"),
        pp_wickets        = ("bowler_wicket",    "sum"),
        pp_dot_balls      = ("is_dot",           "sum"),
        pp_boundaries     = ("is_boundary",      "sum"),
        pp_innings_bowled = ("match_id",         "nunique")
    ).reset_index().rename(columns={"bowler": "player_name"})

    # Overs bowled (balls / 6, rounded to 1 decimal) - Powerplay
    pp_bowling_stats["pp_over"], pp_bowling_stats["pp_ball"] = pp_bowling_stats["pp_balls_bowled"].divmod(6)
    pp_bowling_stats["pp_overs_bowled"] = (pp_bowling_stats["pp_over"].astype(int).astype(str) + '.' + pp_bowling_stats["pp_ball"].astype(int).astype(str)).astype(float)

    # Economy rate = runs conceded per over - Powerplay
    pp_bowling_stats["pp_economy"] = (
        pp_bowling_stats["pp_runs_conceded"] / pp_bowling_stats["pp_balls_bowled"] * 6
    ).round(2)

    # Bowling average = runs conceded per wicket - Powerplay
    pp_bowling_stats["pp_bowling_average"] = (
        pp_bowling_stats["pp_runs_conceded"] / pp_bowling_stats["pp_wickets"].replace(0, float("nan"))
    ).round(2)

    # Bowling strike rate = balls bowled per wicket - Powerplay
    pp_bowling_stats["pp_bowling_strike_rate"] = (
    pp_bowling_stats["pp_balls_bowled"] / pp_bowling_stats["pp_wickets"].replace(0, float("nan"))
    ).round(2)

     # Boundary percentage = legal deliveries hit for 4 or 6
    pp_bowling_stats["pp_boundary_pct"] = (pp_bowling_stats["pp_boundaries"] / pp_bowling_stats["pp_balls_bowled"] * 100).fillna(0).round(2)

    # Balls per boundary  = (Boundary percentage/100)^(-1)
    pp_bowling_stats["pp_balls_per_boundary"] = (
    (pp_bowling_stats["pp_balls_bowled"] / pp_bowling_stats["pp_boundaries"])
    .replace([float('inf'), float('-inf')], 0)
    .astype(int)
)

    ## ----------------------------------------------------
    ## MIDDLE PERIOD BOWLING STATS
    ## ----------------------------------------------------
    middle_bowling_stats = deliveries_df[deliveries_df["is_middle"] == 1].groupby("bowler").agg(
        middle_balls_bowled   = ("is_legal",        "sum"),
        middle_runs_conceded  = ("runs_conceded",    "sum"),
        middle_wickets        = ("bowler_wicket",    "sum"),
        middle_dot_balls      = ("is_dot",           "sum"),
        middle_boundaries     = ("is_boundary",      "sum"),
        middle_innings_bowled = ("match_id",         "nunique")
    ).reset_index().rename(columns={"bowler": "player_name"})

    # Overs bowled (balls / 6, rounded to 1 decimal) - Middle Overs
    middle_bowling_stats["middle_over"], middle_bowling_stats["middle_ball"] = middle_bowling_stats["middle_balls_bowled"].divmod(6)
    middle_bowling_stats["middle_overs_bowled"] = (middle_bowling_stats["middle_over"].astype(int).astype(str) + '.' + middle_bowling_stats["middle_ball"].astype(int).astype(str)).astype(float)

    # Economy rate = runs conceded per over - Middle Overs
    middle_bowling_stats["middle_economy"] = (
        middle_bowling_stats["middle_runs_conceded"] / middle_bowling_stats["middle_balls_bowled"] * 6
    ).round(2)

    # Bowling average = runs conceded per wicket - Middle Overs
    middle_bowling_stats["middle_bowling_average"] = (
        middle_bowling_stats["middle_runs_conceded"] / middle_bowling_stats["middle_wickets"].replace(0, float("nan"))
    ).round(2)

    # Bowling strike rate = balls bowled per wicket - Middle Overs
    middle_bowling_stats["middle_bowling_strike_rate"] = (
    middle_bowling_stats["middle_balls_bowled"] / middle_bowling_stats["middle_wickets"].replace(0, float("nan"))
    ).round(2)

     # Boundary percentage = legal deliveries hit for 4 or 6
    middle_bowling_stats["middle_boundary_pct"] = (middle_bowling_stats["middle_boundaries"] / middle_bowling_stats["middle_balls_bowled"] * 100).fillna(0).round(2)

    # Balls per boundary  = (Boundary percentage/100)^(-1)
    middle_bowling_stats["middle_balls_per_boundary"] = (
    (middle_bowling_stats["middle_balls_bowled"] / middle_bowling_stats["middle_boundaries"])
    .replace([float('inf'), float('-inf')], 0)
    .astype(int)
)

    ## ----------------------------------------------------
    ## DEATH PERIOD BOWLING STATS
    ## ----------------------------------------------------
    death_bowling_stats = deliveries_df[deliveries_df["is_death"] == 1].groupby("bowler").agg(
        death_balls_bowled   = ("is_legal",        "sum"),
        death_runs_conceded  = ("runs_conceded",    "sum"),
        death_wickets        = ("bowler_wicket",    "sum"),
        death_dot_balls      = ("is_dot",           "sum"),
        death_boundaries     = ("is_boundary",      "sum"),
        death_innings_bowled = ("match_id",         "nunique")
    ).reset_index().rename(columns={"bowler": "player_name"})

    # Overs bowled (balls / 6, rounded to 1 decimal) - Death Overs
    death_bowling_stats["death_over"], death_bowling_stats["death_ball"] = death_bowling_stats["death_balls_bowled"].divmod(6)
    death_bowling_stats["death_overs_bowled"] = (death_bowling_stats["death_over"].astype(int).astype(str) + '.' + death_bowling_stats["death_ball"].astype(int).astype(str)).astype(float)

    # Economy rate = runs conceded per over -  Death Overs
    death_bowling_stats["death_economy"] = (
        death_bowling_stats["death_runs_conceded"] / death_bowling_stats["death_balls_bowled"] * 6
    ).round(2)

    # Bowling average = runs conceded per wicket - Death Overs
    death_bowling_stats["death_bowling_average"] = (
        death_bowling_stats["death_runs_conceded"] / death_bowling_stats["death_wickets"].replace(0, float("nan"))
    ).round(2)

    # Bowling strike rate = balls bowled per wicket - Death Overs
    death_bowling_stats["death_bowling_strike_rate"] = (
    death_bowling_stats["death_balls_bowled"] / death_bowling_stats["death_wickets"].replace(0, float("nan"))
    ).round(2)

     # Boundary percentage = legal deliveries hit for 4 or 6
    death_bowling_stats["death_boundary_pct"] = (death_bowling_stats["death_boundaries"] / death_bowling_stats["death_balls_bowled"] * 100).fillna(0).round(2)

    # Balls per boundary  = (Boundary percentage/100)^(-1)
    death_bowling_stats["death_balls_per_boundary"] = (
    (death_bowling_stats["death_balls_bowled"] / death_bowling_stats["death_boundaries"])
    .replace([float('inf'), float('-inf')], 0)
    .astype(int)
)
    
    player_bowling_stats_df = (players_df
        .merge(bowling_stats,  on="player_name", how="left"))

    master_bowling_df = pp_bowling_stats.merge(middle_bowling_stats, on="player_name", how="outer")
    master_bowling_df = master_bowling_df.merge(death_bowling_stats, on="player_name", how="outer")
    master_bowling_df.fillna(0, inplace=True)

    player_bowling_stats_df = (player_bowling_stats_df.merge(master_bowling_df, on="player_name", how="outer"))
     
    print(f"✓ Player stats calculated: {len(player_bowling_stats_df)} players")
    # print(f"  Columns: {list(player_bowling_stats_df.columns)}")

    return player_bowling_stats_df

# # # Bowling stats for regular season
# player_bowling_stats_df = calculate_bowling_stats(deliveries_df=deliveries_df, players_df=players_df)
# player_bowling_stats_df= player_bowling_stats_df[(player_bowling_stats_df["team"].notna())]
# # print(player_bowling_stats_df)

# # # Bowling stats for playoff
# playoff_player_bowling_stats_df = calculate_bowling_stats(deliveries_df=playoff_deliveries_df, players_df=playoff_players_df)
# playoff_player_bowling_stats_df= playoff_player_bowling_stats_df[(playoff_player_bowling_stats_df["team"].notna())]
# # print(playoff_player_bowling_stats_df)

# # # Bowling stats for playoff
# whole_player_bowling_stats_df = calculate_bowling_stats(deliveries_df=whole_deliveries_df, players_df=whole_players_df)
# whole_player_bowling_stats_df= whole_player_bowling_stats_df[(whole_player_bowling_stats_df["team"].notna())]




# print("\n")
# print(whole_player_bowling_stats_df[whole_player_bowling_stats_df["player_name"].str.contains("Archer")])

# print("\n")
# print(playoff_player_bowling_stats_df[playoff_player_bowling_stats_df["player_name"].str.contains("Archer")])

# print("\n")
# print(whole_player_bowling_stats_df[whole_player_bowling_stats_df["player_name"].str.contains("Rabada")])

# print("\n")
# print(playoff_player_bowling_stats_df[playoff_player_bowling_stats_df["player_name"].str.contains("Rabada")])

# print("\n")
# print(player_bowling_stats_df[player_bowling_stats_df["player_name"].str.contains("Holder")])

# print("\n")
# print(player_bowling_stats_df[player_bowling_stats_df["player_name"].str.contains("Bumrah")])

# print("\n")
# print(player_bowling_stats_df[player_bowling_stats_df["player_name"].str.contains("Narine")])

# -------------------------------------------------------------------------------------
def calculate_team_stats(matches_df, player_batting_stats_df, player_bowling_stats_df, deliveries_df):
    """
    Calculates overall season stats for every team from the deliveries DataFrame.
    Returns a single team_stats_df with one row per player containing:
      - Matches played, won, lost or no - result
      - Points in reg season
      - Win percentage
      - Net Run Rate
      - Total Runs 
      - Team Batting Average
      - Batting Strike Rate
      - Fours and Sixes hit
      - Balls per Boundary Hit
      - Total Runs Conceded (Bowling)
      - Wickets
      - Economy Rate
      - Bowling Average
      - Dot Ball Percentage
      - Bowling Strike Rate
      - Runs, Batting SR, Boundaries, Balls per Boundary for each innings phase
      - Runs Conceded, Wickets, Econ Rate, Bowling Avg, Dot Ball pct, Bowling SR, balls per boundary for
          - each innings phase 
          
          
          (Insert deliveries_df and matches_df as input parameters)"""

    # all_matches.append({
    #             "match_id": match_id,
    #             "city": match_city,
    #             "date": match_date,
    #             "number": match_number,
    #             "winner": match_winner,
    #             "outcome": match_outcome,
    #             "wickets_runs": match_outcome_w_r,
    #             "winning_amount": match_outcome_amt,
    #             "toss_winner": match_toss_winner,
    #             "toss_decision": match_toss_decision,
    #             "venue": match_venue,
    #             "team1": team_1,
    #             "team2": team_2}
    #  )

               

#     # -------------------------------------------------------
#     # TABLE STATS
#     # grouped by team
#     # -------------------------------------------------------
    
    team1_df = matches_df[["match_id", "date", "team1", "winner"]].rename(columns={'team1': 'team_name'})
    team2_df = matches_df[["match_id", "date", "team2", "winner"]].rename(columns={'team2': 'team_name'})

    team_match_df = pd.concat([team1_df, team2_df], ignore_index=True)
    team_match_df = team_match_df.sort_values(by=["team_name", "date"]).reset_index(drop=True)
    team_match_df["game_result"] = np.where(team_match_df["team_name"] == team_match_df["winner"], 'W', (np.where(team_match_df["winner"] == "NR", 'NR', 'L')))
    

    #     # Number of games played, won and no result by team
    team_stats = matches_df.groupby("team_name").agg(
        match_num =("match_id",     "nunique"),
        match_won =("is_win",       "sum"),
        match_nr =("no_result_flag",    "sum")

    ).reset_index()

    team_stats["match_loss"] = team_stats["match_num"] - team_stats["match_won"] - team_stats["match_nr"]
    team_stats["points"] = (team_stats["match_won"] * 2) + team_stats["match_nr"]
    team_stats["win_pct"] = team_stats["match_won"] / team_stats["match_num"]

    team_stats = team_stats.sort_values(by="points", ascending=False).reset_index(drop=True)

    # Check to find out how many matches a team got bowled out
    bowled_out = deliveries_df[(deliveries_df["player_out"] != "") & (~deliveries_df["wicket_kind"].isin(["retired hurt"]))].groupby(["match_id", "team"]).agg(
        match_dismissals = ("player_out",   "count")
    ).reset_index().rename(columns= {"team": "team_name"})

    bowled_out["match_all_out"] = np.where(bowled_out["match_dismissals"] == 10, 1, 0)
    # bowled_out["nrr_overs"] = np.where("match_all_out" == 1, 20, )

    team_all_out = bowled_out.groupby("team_name").agg(
        matches_all_out = ("match_dismissals",  "sum"),
        total_match_dismissals = ("match_all_out",   "sum")
    ).reset_index()


   # Aggregate batting statistics for entire team
    team_season_batting_stats = player_batting_stats_df.groupby("team").agg(
        team_runs =     ("runs",        "sum"),
        team_balls_faced = ("balls_faced",  "sum"),
        team_dot_balls  =  ("dot_balls",    "sum"),
        team_fours      =  ("fours",        "sum"),
        team_sixes      =  ("sixes",        "sum"),
        team_dismissals =  ("dismissals",   "sum"),
        team_pp_runs = ("pp_runs",           "sum"),
        team_pp_dot_balls = ("pp_dot_balls", "sum"),
        team_pp_fours = ("pp_fours",         "sum"),
        team_pp_sixes = ("pp_sixes",         "sum"),
        team_middle_runs = ("middle_runs",   "sum"),
        team_middle_dot_balls = ("middle_dot_balls", "sum"),
        team_middle_fours = ("middle_fours", "sum"),
        team_middle_sixes = ("middle_sixes", "sum"),
        team_death_runs = ("death_runs",        "sum"),
        team_death_dot_balls = ("death_dot_balls", "sum"),
        team_death_fours = ("death_fours",   "sum"),
        team_death_sixes = ("death_sixes",   "sum"),
        team_pp_strike_rate = ("pp_strike_rate",    "mean"),
        team_middle_strike_rate = ("middle_strike_rate",      "mean"),
        team_death_strike_rate = ("death_strike_rate",       "mean"),
        team_pp_boundary_pct = ("pp_boundary_pct",   "mean"),
        team_middle_boundary_pct = ("middle_boundary_pct",   "mean"),
        team_death_boundary_pct = ("death_boundary_pct",   "mean"),
        team_pp_dot_ball_pct = ("pp_dot_ball_pct",   "mean"),
        team_middle_dot_ball_pct = ("middle_dot_ball_pct",   "mean"),
        team_death_dot_ball_pct = ("death_dot_ball_pct",   "mean"),


    ).reset_index().rename(columns={"team": "team_name"})

    team_season_batting_stats["team_boundary_pct"] = ((team_season_batting_stats["team_fours"] + team_season_batting_stats["team_sixes"]) / (team_season_batting_stats["team_balls_faced"]) * 100).round(2)
    team_season_batting_stats["team_dot_ball_pct"] = (team_season_batting_stats["team_dot_balls"] / team_season_batting_stats["team_balls_faced"] * 100).round(2)
    team_season_batting_stats["team_batting_avg"] = (team_season_batting_stats["team_runs"] / team_season_batting_stats["team_dismissals"]).round(2)
    team_season_batting_stats["team_batting_strike_rate"] = (team_season_batting_stats["team_runs"] / team_season_batting_stats["team_balls_faced"]).round(2)

    team_season_batting_stats = pd.merge(team_season_batting_stats, team_all_out, how="outer", on="team_name")

   
    team_season_bowling_stats = player_bowling_stats_df.groupby("team").agg(
        team_runs_conceded = ("runs_conceded",      "sum"),
        team_balls_bowled =  ("balls_bowled",       "sum"),
        team_wickets =       ("wickets",            "sum"),
        team_dot_balls_bowled = ("dot_balls",       "sum"),
        team_boundaries_conceded = ("boundaries",   "sum"),
        team_pp_balls_bowled   = ("pp_balls_bowled", "sum"),
        team_pp_runs_conceded  = ("pp_runs_conceded",    "sum"),
        team_pp_wickets        = ("pp_wickets",     "sum"),
        team_pp_dot_balls      = ("pp_dot_balls",   "sum"),
        team_pp_boundaries     = ("pp_boundaries",  "sum"),
        team_middle_balls_bowled   = ("middle_balls_bowled", "sum"),
        team_middle_runs_conceded  = ("middle_runs_conceded",    "sum"),
        team_middle_wickets        = ("middle_wickets",     "sum"),
        team_middle_dot_balls      = ("middle_dot_balls",   "sum"),
        team_middle_boundaries     = ("middle_boundaries",  "sum"),
        team_death_balls_bowled   = ("death_balls_bowled", "sum"),
        team_death_runs_conceded  = ("death_runs_conceded",    "sum"),
        team_death_wickets        = ("death_wickets",     "sum"),
        team_death_dot_balls      = ("death_dot_balls",   "sum"),
        team_death_boundaries     = ("death_boundaries",  "sum"),
        team_pp_economy           = ("pp_economy",        "mean"),
        team_pp_bowling_average   = ("pp_bowling_average", "mean"),
        team_pp_bowling_strike_rate = ("pp_bowling_strike_rate", "mean"),
        team_pp_boundary_pct = ("pp_boundary_pct",        "mean"),
        team_pp_balls_per_boundary = ("pp_balls_per_boundary",  "mean"),
        team_middle_economy           = ("middle_economy",        "mean"),
        team_middle_bowling_average   = ("middle_bowling_average", "mean"),
        team_middle_bowling_strike_rate = ("middle_bowling_strike_rate", "mean"),
        team_middle_boundary_pct = ("middle_boundary_pct",        "mean"),
        team_middle_balls_per_boundary = ("middle_balls_per_boundary",  "mean"),
        team_death_economy           = ("death_economy",        "mean"),
        team_death_bowling_average   = ("death_bowling_average", "mean"),
        team_death_bowling_strike_rate = ("death_bowling_strike_rate", "mean"),
        team_death_boundary_pct = ("death_boundary_pct",        "mean"),
        team_death_balls_per_boundary = ("death_balls_per_boundary",  "mean")
    ).reset_index().rename(columns={"team": "team_name"})

    team_season_bowling_stats["team_economy"] = (team_season_bowling_stats["team_runs_conceded"] / team_season_bowling_stats["team_balls_bowled"] * 6).round(2)
    team_season_bowling_stats["team_bowling_avg"] = (team_season_bowling_stats["team_runs_conceded"] / team_season_bowling_stats["team_wickets"]).replace(0, float("nan")).round(2)
    team_season_bowling_stats["team_bowling_strike_rate"] = (team_season_bowling_stats["team_balls_bowled"] / team_season_bowling_stats["team_wickets"]).replace(0, float("nan")).round(2)
    team_season_bowling_stats["team_dot_ball_pct"] = (team_season_bowling_stats["team_boundaries_conceded"] / team_season_bowling_stats["team_balls_bowled"] * 100).round(2)
    
    team_season_batting_stats["team_net_run_rate"] = team_season_bowling_stats["team_runs_conceded"]

#     # Dot balls = legal delivery where total runs == 0
#     deliveries_df["total_runs"] = deliveries_df["runs_off_bat"] + deliveries_df["extras"]
#     deliveries_df["is_dot"] = (
#         (deliveries_df["is_legal"] == 1) & (deliveries_df["total_runs"] == 0)
#     ).astype(int)

#     bowling_stats = deliveries_df.groupby("bowler").agg(
#         balls_bowled   = ("is_legal",        "sum"),
#         runs_conceded  = ("runs_conceded",    "sum"),
#         wickets        = ("bowler_wicket",    "sum"),
#         dot_balls      = ("is_dot",           "sum"),
#         innings_bowled = ("match_id",         "nunique")
#     ).reset_index().rename(columns={"bowler": "player_name"})

#     # Overs bowled (balls / 6, rounded to 1 decimal)
#     bowling_stats["overs_bowled"] = (
#         bowling_stats["balls_bowled"] / 6
#     ).round(1)

#     # Economy rate = runs conceded per over
#     bowling_stats["economy"] = (
#         bowling_stats["runs_conceded"] / bowling_stats["overs_bowled"]
#     ).round(2)

#     # Bowling average = runs conceded per wicket
#     bowling_stats["bowling_average"] = (
#         bowling_stats["runs_conceded"] / bowling_stats["wickets"].replace(0, float("nan"))
#     ).round(2)

#     # Bowling strike rate = balls bowled per wicket
#     bowling_stats["bowling_strike_rate"] = (
#     bowling_stats["balls_bowled"] / bowling_stats["wickets"].replace(0, float("nan"))
#     ).round(2)


#     # -------------------------------------------------------
#     # FIELDING STATS
#     # -------------------------------------------------------

#     # Caught and bowled — catch credited to the bowler
#     catches_cb = deliveries_df[
#         deliveries_df["wicket_type"] == "caught and bowled"
#     ].groupby("bowler").size().reset_index()
#     catches_cb.columns = ["player_name", "catches_cb"]

#     # Normal catches — fielder is in other_player_dismissed
#     catches_normal = deliveries_df[
#         deliveries_df["wicket_type"] == "caught"
#     ].groupby("other_player_dismissed").size().reset_index()
#     catches_normal.columns = ["player_name", "catches_normal"]

#     # Run outs — credited to fielder in other_player_dismissed
#     run_outs = deliveries_df[
#         deliveries_df["wicket_type"] == "run out"
#     ].groupby("other_player_dismissed").size().reset_index()
#     run_outs.columns = ["player_name", "run_outs"]

#     # Stumpings — credited to wicketkeeper in other_player_dismissed
#     stumpings = deliveries_df[
#         deliveries_df["wicket_type"] == "stumped"
#     ].groupby("other_player_dismissed").size().reset_index()
#     stumpings.columns = ["player_name", "stumpings"]

#     # Combine all fielding stats
#     fielding_stats = (catches_normal
#         .merge(catches_cb,  on="player_name", how="outer")
#         .merge(run_outs,    on="player_name", how="outer")
#         .merge(stumpings,   on="player_name", how="outer")
#         .fillna(0)
#     )
#     fielding_stats["catches"] = (
#         fielding_stats["catches_normal"] + fielding_stats["catches_cb"]
#     ).astype(int)
#     fielding_stats = fielding_stats[["player_name", "catches", "run_outs", "stumpings"]]


#     # -------------------------------------------------------
#     # JOIN EVERYTHING TOGETHER
#     # -------------------------------------------------------
#     player_stats_df = (players_df
#         .merge(batting_stats,  on="player_name", how="left")
#         .merge(bowling_stats,  on="player_name", how="left")
#         .merge(fielding_stats, on="player_name", how="left")
#         .fillna(0)
#     )

#     print(f"✓ Player stats calculated: {len(player_stats_df)} players")
#     print(f"  Columns: {list(player_stats_df.columns)}")

#     return player_stats_df

# # %%
# player_stats_df = calculate_player_stats(deliveries_df, players_df)


# # %%
# def calculate_innings_stats(deliveries_df):
#     """
#     Calculates per-innings stats for each player.
#     Used to derive:
#       Batting: highest score (with not out *), 50s, 100s
#       Bowling: best bowling figures, 4 wicket hauls, 5 wicket hauls

#     Returns:
#       batting_innings_df : one row per batter per match per innings
#       bowling_innings_df : one row per bowler per match per innings
#     """

#     # -------------------------------------------------------
#     # BATTING INNINGS STATS
#     # group by match + innings + striker
#     # -------------------------------------------------------

#     # Reuse ball_faced and is_four, is_six if already calculated
#     # otherwise calculate them here too
#     if "ball_faced" not in deliveries_df.columns:
#         deliveries_df["ball_faced"] = deliveries_df["wides"].isna().astype(int)
#     if "is_four" not in deliveries_df.columns:
#         deliveries_df["is_four"] = (deliveries_df["runs_off_bat"] == 4).astype(int)
#     if "is_six" not in deliveries_df.columns:
#         deliveries_df["is_six"] = (deliveries_df["runs_off_bat"] == 6).astype(int)

#     batting_innings_df = deliveries_df.groupby(
#         ["match_id", "innings", "striker"]
#     ).agg(
#         runs        = ("runs_off_bat", "sum"),
#         balls_faced = ("ball_faced",   "sum"),
#         fours       = ("is_four",      "sum"),
#         sixes       = ("is_six",       "sum"),
#     ).reset_index().rename(columns={"striker": "player_name"})

#     # Determine if batter was dismissed in this innings
#     # by checking if their name appears in player_dismissed
#     # for the same match and innings
#     dismissals = (deliveries_df[deliveries_df["player_dismissed"].notna()]
#                     [["match_id", "innings", "player_dismissed"]]
#                     .drop_duplicates()
#                     .rename(columns={"player_dismissed": "player_name"}))
#     dismissals["was_dismissed"] = True

#     batting_innings_df = batting_innings_df.merge(
#         dismissals,
#         on=["match_id", "innings", "player_name"],
#         how="left"
#     )
#     batting_innings_df["was_dismissed"] = batting_innings_df["was_dismissed"].fillna(False)

#     # Format highest score with * for not out
#     batting_innings_df["score_str"] = batting_innings_df.apply(
#         lambda row: str(int(row["runs"])) if row["was_dismissed"] else str(int(row["runs"])) + "*",
#         axis=1
#     )

#     # Flag 50s and 100s
#     # 50 = runs >= 50 and < 100
#     # 100 = runs >= 100
#     batting_innings_df["is_fifty"]   = (
#         (batting_innings_df["runs"] >= 50) & (batting_innings_df["runs"] < 100)
#     ).astype(int)
#     batting_innings_df["is_hundred"] = (
#         batting_innings_df["runs"] >= 100
#     ).astype(int)


#     # -------------------------------------------------------
#     # BOWLING INNINGS STATS
#     # group by match + innings + bowler
#     # -------------------------------------------------------

#     if "is_legal" not in deliveries_df.columns:
#         deliveries_df["is_legal"] = (
#             deliveries_df["wides"].isna() & deliveries_df["noballs"].isna()
#         ).astype(int)

#     if "runs_conceded" not in deliveries_df.columns:
#         deliveries_df["runs_conceded"] = (
#             deliveries_df["runs_off_bat"].fillna(0) +
#             deliveries_df["wides"].fillna(0) +
#             deliveries_df["noballs"].fillna(0)
#         )

#     if "bowler_wicket" not in deliveries_df.columns:
#         deliveries_df["bowler_wicket"] = (
#             deliveries_df["wicket_type"].notna() &
#             ~deliveries_df["wicket_type"].isin([
#                 "run out", "retired hurt", "retired out", "obstructing the field"
#             ])
#         ).astype(int)

#     bowling_innings_df = deliveries_df.groupby(
#         ["match_id", "innings", "bowler"]
#     ).agg(
#         balls_bowled  = ("is_legal",       "sum"),
#         runs_conceded = ("runs_conceded",  "sum"),
#         wickets       = ("bowler_wicket",  "sum"),
#     ).reset_index().rename(columns={"bowler": "player_name"})

#     # Flag 4 wicket and 5 wicket hauls
#     bowling_innings_df["is_four_wickets"] = (
#         (bowling_innings_df["wickets"] >= 4) & (bowling_innings_df["wickets"] < 5)
#     ).astype(int)
#     bowling_innings_df["is_five_wickets"] = (
#         bowling_innings_df["wickets"] >= 5
#     ).astype(int)

#     # Best bowling figures as string e.g. "4/22"
#     bowling_innings_df["figures_str"] = (
#         bowling_innings_df["wickets"].astype(int).astype(str) + "/" +
#         bowling_innings_df["runs_conceded"].astype(int).astype(str)
#     )

#     return batting_innings_df, bowling_innings_df


# def calculate_milestones(batting_innings_df, bowling_innings_df):
#     """
#     Aggregates innings-level data into per-player milestone stats:
#       Batting : highest_score, fifties, hundreds
#       Bowling : best_figures, four_wicket_hauls, five_wicket_hauls
#     """

#     # -------------------------------------------------------
#     # BATTING MILESTONES
#     # -------------------------------------------------------

#     # Highest score — sort by runs desc, not out ranks above out for equal runs
#     batting_innings_df["not_out"] = (~batting_innings_df["was_dismissed"]).astype(int)

#     highest_score = (batting_innings_df
#         .sort_values(["runs", "not_out"], ascending=[False, False])
#         .groupby("player_name")
#         .first()[["score_str"]]
#         .reset_index()
#         .rename(columns={"score_str": "highest_score"})
#     )

#     # Count 50s and 100s per player
#     batting_milestones = batting_innings_df.groupby("player_name").agg(
#         fifties  = ("is_fifty",   "sum"),
#         hundreds = ("is_hundred", "sum"),
#     ).reset_index()

#     batting_milestones = batting_milestones.merge(highest_score, on="player_name", how="left")


#     # -------------------------------------------------------
#     # BOWLING MILESTONES
#     # -------------------------------------------------------

#     # Best bowling figures — sort by wickets desc, then runs asc (fewer runs is better)
#     best_figures = (bowling_innings_df
#         .sort_values(["wickets", "runs_conceded"], ascending=[False, True])
#         .groupby("player_name")
#         .first()[["figures_str"]]
#         .reset_index()
#         .rename(columns={"figures_str": "best_figures"})
#     )

#     # Count 4 and 5 wicket hauls per player
#     bowling_milestones = bowling_innings_df.groupby("player_name").agg(
#         four_wicket_hauls = ("is_four_wickets", "sum"),
#         five_wicket_hauls = ("is_five_wickets", "sum"),
#     ).reset_index()

#     bowling_milestones = bowling_milestones.merge(best_figures, on="player_name", how="left")

#     return batting_milestones, bowling_milestones

# # %%
# batting_innings_df, bowling_innings_df = calculate_innings_stats(deliveries_df)

# # %%
# batting_milestones, bowling_milestones = calculate_milestones(batting_innings_df, bowling_innings_df)

# # %%
# player_stats_df = player_stats_df.merge(batting_milestones, on="player_name", how='left')
# player_stats_df = player_stats_df.merge(bowling_milestones, on="player_name", how='left')

# # %%
# player_stats_df

# # %%
# matches_df[matches_df['match_number']=='50']

# # %% [markdown]
# # 


