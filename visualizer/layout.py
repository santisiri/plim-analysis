from dash import html, dcc
import dash_bootstrap_components as dbc
from .components.advanced_analysis import create_advanced_analysis_figures, create_summary_stats

def create_analysis_tab(analysis_results):
    summary_stats = create_summary_stats(analysis_results)
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Analysis Summary"),
                dbc.Card([
                    dbc.CardBody([
                        html.P(f"Tempo Stability: {summary_stats['tempo_stability']}"),
                        html.P(f"Rhythm Strength: {summary_stats['rhythm_strength']}"),
                        html.P(f"Number of Segments: {summary_stats['num_segments']}"),
                        html.P(f"Average Segment Duration: {summary_stats['avg_segment_duration']}"),
                        html.P(f"Pitch Variability: {summary_stats['pitch_variability']}"),
                        html.P(f"Energy Variance: {summary_stats['energy_variance']}")
                    ])
                ])
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    figure=create_advanced_analysis_figures(analysis_results),
                    style={'height': '1200px'}
                )
            ], width=12)
        ])
    ]) 