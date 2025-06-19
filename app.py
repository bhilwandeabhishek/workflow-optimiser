import pandas as pd
from collections import Counter
import os
import json

# Update SLA limits as needed
SLA_LIMITS = {
   'Created': 30,
   'Assigned': 30,
   'In Progress': 240,
   'Waiting for Customer': 1440,
   'Code Review': 180,
   'QA Review': 180,
   'Resolved': 60,
   'Closed': 60,
   'Reopened': 120
}

OUTPUT_DIR = "output"

def save_json(data, filename):
   os.makedirs(OUTPUT_DIR, exist_ok=True)
   path = os.path.join(OUTPUT_DIR, filename)
   with open(path, 'w') as f:
       json.dump(data, f, indent=2)
   print(f"Saved: {path}")

def load_log(filepath):
   try:
       df = pd.read_csv(filepath)
       df.columns = [col.lower().strip() for col in df.columns]
       df['timestamp'] = pd.to_datetime(df['timestamp'])
       df = df.sort_values(by=['case_id', 'timestamp'])
       # Check for new columns
       if 'role' not in df.columns or 'story_points' not in df.columns:
           raise ValueError("Missing required columns: role or story_points")
       return df
   except Exception as e:
       print(f"Error loading file: {e}")
       return None

def show_common_paths(df):
   variants = df.groupby('case_id')['activity'].apply(list)
   variant_strings = variants.apply(lambda x: ' -> '.join(x))
   counter = Counter(variant_strings)

   top_variants = [
       {"path": path, "count": count}
       for path, count in counter.most_common(5)
   ]
   save_json(top_variants, "common_paths.json")

def show_step_durations(df):
   df['duration'] = df.groupby('case_id')['timestamp'].diff()
   avg_durations = df.groupby('activity')['duration'].mean().dropna()
   avg_story_points = df.groupby('activity')['story_points'].mean().dropna()

   durations = []
   for step, dur in avg_durations.items():
       mins = round(dur.total_seconds() / 60, 2)
       sp = round(avg_story_points.get(step, 0), 2)
       durations.append({
           "step": step,
           "average_minutes": mins,
           "average_story_points": sp,
           "bottleneck": mins > 60
       })

   save_json(durations, "step_durations.json")

def show_user_delays(df):
   df_filtered = df.dropna(subset=['duration', 'user', 'role', 'story_points'])

   grouped = df_filtered.groupby(['user', 'role', 'activity'])
   detailed_stats = []

   for (user, role, activity), group in grouped:
       avg_duration = group['duration'].mean().total_seconds() / 60
       avg_story_points = group['story_points'].mean()
       cases = group['case_id'].unique().tolist()
       detailed_stats.append({
           "user": user,
           "role": role,
           "activity": activity,
           "average_minutes": round(avg_duration, 2),
           "average_story_points": round(avg_story_points, 2),
           "occurrences": len(group),
           "cases": cases[:5],
           "more_cases": len(cases) > 5
       })

   user_durations = df_filtered.groupby('user')['duration'].mean()
   slowest_user = user_durations.idxmax()
   slowest_time = round(user_durations.max().total_seconds() / 60, 2)

   result = {
       "user_stats": detailed_stats,
       "slowest_user": {
           "user": slowest_user,
           "average_minutes": slowest_time
       }
   }

   save_json(result, "user_delays.json")

def show_case_durations(df):
   case_durations = df.groupby('case_id')['timestamp'].agg(['min', 'max'])
   case_durations['total_duration'] = (case_durations['max'] - case_durations['min']).dt.total_seconds() / 60

   durations = [
       {"case_id": idx, "total_minutes": round(row['total_duration'], 2)}
       for idx, row in case_durations.iterrows()
   ]

   slowest_case = case_durations['total_duration'].idxmax()
   slowest_time = round(case_durations['total_duration'].max(), 2)

   result = {
       "cases": durations,
       "slowest_case": {
           "case_id": slowest_case,
           "duration_minutes": slowest_time
       }
   }

   save_json(result, "case_durations.json")

def show_sla_violations(df):
   df['duration_mins'] = df['duration'].dt.total_seconds() / 60
   violations = []

   for _, row in df.dropna(subset=['duration']).iterrows():
       activity = row['activity']
       mins = row['duration_mins']
       limit = SLA_LIMITS.get(activity)
       if limit and mins > limit:
           violations.append({
               "case_id": row['case_id'],
               "activity": activity,
               "user": row['user'],
               "role": row['role'],
               "duration_minutes": round(mins),
               "sla_limit": limit,
               "story_points": row['story_points']
           })

   save_json(violations, "sla_violations.json")

def save_cleaned_log(df, output_path="output/cleaned_log.csv"):
   os.makedirs("output", exist_ok=True)
   df.to_csv(output_path, index=False)
   print(f"Cleaned log saved to {output_path}")

def prepare_data(df):
   df['step'] = df.groupby('case_id').cumcount()
   df['duration'] = df.groupby('case_id')['timestamp'].diff()
   return df

def main():
   print("Enterprise Workflow Optimizer (JSON Output Mode)")
   path = "data.csv"  # Updated for new data file

   if not os.path.exists(path):
       print(f"File not found: {path}")
       return

   df = load_log(path)
   if df is None:
       return

   df = prepare_data(df)
   show_user_delays(df)
   show_case_durations(df)
   show_sla_violations(df)
   show_common_paths(df)
   show_step_durations(df)

if __name__ == "_main_":
   main()