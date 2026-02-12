import matplotlib.pyplot as plt
import pandas as pd

def create_match_chart(breakdown_scores, output_path="match_chart.png"):
    """Create a radar chart of match scores"""
    categories = list(breakdown_scores.keys())
    scores = list(breakdown_scores.values())
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Create bar chart
    bars = ax.barh(categories, scores, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
    
    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                f'{width:.1f}%', ha='left', va='center')
    
    ax.set_xlim(0, 100)
    ax.set_xlabel('Match Percentage')
    ax.set_title('Resume-JD Match Breakdown')
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()
    
    return output_path