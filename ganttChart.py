from flask import render_template
import plotly.figure_factory as ff
from datetime import datetime, timedelta
from models import Task, db

def create_gantt_chart():
    # タスク一覧を取得
    tasks = Task.query.all()
    
    # ガントチャートのデータを作成
    df = []
    
    for task in tasks:
        # 開始日が設定されていない場合は現在日時を使用
        start = task.start_date if task.start_date else datetime.now()
        # 期限が設定されていない場合は開始日から1日後を使用
        finish = task.due_date if task.due_date else (start + timedelta(days=1))
        
        df.append(dict(
            Task=task.title,
            Start=start,
            Finish=finish,
            Status=task.status,
        ))
    
    if not df:  # タスクが存在しない場合
        return None
    
    # ガントチャートの作成
    colors = {
        'todo': 'rgb(220, 0, 0)',      # 赤
        'doing': 'rgb(255, 165, 0)',   # オレンジ
        'done': 'rgb(0, 255, 0)'       # 緑
    }

    fig = ff.create_gantt(
        df,
        colors=colors,
        index_col='Status',
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True,
        bar_width=0.3,  # バーの太さを調整
        
    )
    
    # 各バーにボーダーを追加
    for trace in fig['data']:
        trace.update(
            marker=dict(
                line=dict(width=1, color='black')  # 黒い1pxのボーダー
            ),
            opacity=0.8  # 少し透明度を加えて立体感を出す
        )
    
    # レイアウトの設定
    fig.update_layout(
        title='Task Gantt Chart',
        xaxis_title='Date',
        yaxis_title='Task',
        showlegend=True,  # 凡例を表示
        height=400
    )
    
    # HTMLに埋め込むためのJSONデータを返す
    return fig.to_json()
