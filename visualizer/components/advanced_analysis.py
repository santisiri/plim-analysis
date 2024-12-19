import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def create_advanced_analysis_figures(analysis_results):
    # Create subplot figure
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Rhythm Analysis', 'Melodic Content',
            'Temporal Patterns', 'Structural Segments',
            'Feature Distribution', 'Song Clusters'
        )
    )
    
    # 1. Rhythm Analysis
    rhythm_data = analysis_results['rhythm']
    fig.add_trace(
        go.Scatter(
            y=rhythm_data['pulse'],
            name='Rhythm Pulse',
            line=dict(color='blue')
        ),
        row=1, col=1
    )
    
    # 2. Melodic Content
    melody_data = analysis_results['melodic']
    fig.add_trace(
        go.Scatter(
            y=melody_data['melody_contour'],
            name='Melody Contour',
            line=dict(color='red')
        ),
        row=1, col=2
    )
    
    # 3. Temporal Patterns
    temporal_data = analysis_results['temporal']
    fig.add_trace(
        go.Scatter(
            y=temporal_data['trend'],
            name='Trend',
            line=dict(color='green')
        ),
        row=2, col=1
    )
    
    # 4. Structural Segments
    segments = analysis_results['segments']
    for segment in segments['segment_details']:
        fig.add_vrect(
            x0=segment['start_time'],
            x1=segment['end_time'],
            fillcolor="rgba(0,0,255,0.2)",
            layer="below",
            line_width=0,
            row=2, col=2
        )
    
    # 5. Feature Distribution
    fig.add_trace(
        go.Box(
            y=analysis_results['features']['spectral_centroid'],
            name='Spectral Centroid'
        ),
        row=3, col=1
    )
    
    # 6. Song Clusters
    clusters = analysis_results['patterns']['clusters']
    centers = analysis_results['patterns']['cluster_centers']
    fig.add_trace(
        go.Scatter(
            x=[c[0] for c in centers],
            y=[c[1] for c in centers],
            mode='markers',
            marker=dict(size=10, color=list(range(len(centers)))),
            name='Cluster Centers'
        ),
        row=3, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=1200,
        showlegend=True,
        title_text="Advanced Music Analysis"
    )
    
    return fig

def create_summary_stats(analysis_results):
    return {
        'tempo_stability': f"{analysis_results['features']['tempo_stability']:.2f}",
        'rhythm_strength': f"{analysis_results['features']['rhythm_strength']:.2f}",
        'num_segments': len(analysis_results['segments']['segment_details']),
        'avg_segment_duration': f"{np.mean([s['duration'] for s in analysis_results['segments']['segment_details']]):.2f}s",
        'pitch_variability': f"{analysis_results['melodic']['pitch_variability']:.2f}",
        'energy_variance': f"{analysis_results['features']['energy_var']:.2f}"
    } 