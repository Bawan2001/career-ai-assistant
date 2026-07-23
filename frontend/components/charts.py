import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any

def create_ats_score_gauge(score: float) -> go.Figure:
    """Creates a gauge chart for ATS CV overall quality score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Overall ATS Score", 'font': {'size': 20, 'color': "#F8FAFC"}},
        number={'suffix': "/100", 'font': {'color': "#38BDF8"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
            'bar': {'color': "#38BDF8"},
            'bgcolor': "#1E293B",
            'borderwidth': 2,
            'bordercolor': "#334155",
            'steps': [
                {'range': [0, 50], 'color': "#EF4444"},
                {'range': [50, 75], 'color': "#F59E0B"},
                {'range': [75, 100], 'color': "#10B981"}
            ],
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#F8FAFC", 'family': "Inter"},
        height=250,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_ats_breakdown_chart(breakdown: Dict[str, float]) -> go.Figure:
    """Creates a bar chart showing section-by-section breakdown of ATS scoring."""
    categories = list(breakdown.keys())
    scores = list(breakdown.values())
    
    # Format labels
    clean_categories = [c.replace('_', ' ').title() for c in categories]
    
    fig = px.bar(
        x=scores,
        y=clean_categories,
        orientation='h',
        labels={'x': 'Score Component (Max Points)', 'y': 'Evaluation Dimension'},
        title="ATS Score Breakdown by Dimension",
        color=scores,
        color_continuous_scale="Blues"
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#F8FAFC", 'family': "Inter"},
        coloraxis_showscale=False,
        xaxis=dict(showgrid=True, gridcolor='#334155'),
        yaxis=dict(showgrid=False),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_skill_gap_chart(matched_skills: List[str], missing_skills: List[str]) -> go.Figure:
    """Creates a comparison bar chart between matched vs missing target job skills."""
    labels = ['Matched Skills', 'Missing Skills']
    counts = [len(matched_skills), len(missing_skills)]
    
    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=counts,
            marker_color=['#10B981', '#EF4444'],
            text=counts,
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Target Job Skill Match vs Gap Comparison",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#F8FAFC", 'family': "Inter"},
        yaxis=dict(showgrid=True, gridcolor='#334155'),
        height=280,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
