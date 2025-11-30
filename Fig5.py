

import matplotlib.pyplot as plt
import numpy as np
import os
from tqdm import tqdm
from matplotlib.lines import Line2D

# Create output directory for plots
os.makedirs('fig5_plots', exist_ok=True)

# Figure dimensions for the entire grid
GRID_DIMENSIONS = (16, 12)  # Large figure to accommodate 3x4 grid

# Configuration based on the paper
NUM_NODES = [5, 10, 20]
CONTENTION_LEVELS = {
    'high': 20,      # 20 locks (keys)
    'medium': 100,   # 100 locks (keys)
    'low': 1000      # 1000 locks (keys)
}
LOCALITY_PERCENTAGES = [85, 90, 95]  # For columns 1-3
THREADS_PER_NODE = [2, 4, 6, 8, 10, 12]  # X-axis values (matching paper: 2, 4, 6, 8, 10, 12)

# System names (matching paper: ALock, MCS, Spin)
SYSTEMS = ['ALock', 'MCS', 'Spin']

# System styling for columns 1-3 (with locality variations)
# Format: (color, marker, base_linestyle)
SYSTEM_STYLE_COLS1_3 = {
    'ALock': ('#1f77b4', 's', '-'),      # Blue, square, solid (will vary by locality)
    'MCS': ('#ff7f0e', 'x', '--'),       # Orange, x, dashed
    'Spin': ('#2ca02c', 'o', ':')        # Green, circle, dotted
}

# System styling for column 4 (100% Local)
SYSTEM_STYLE_COL4 = {
    'ALock': ('purple', 'o', '-'),       # Purple, circle, solid (will vary by contention)
    'MCS': ('pink', 's', '--'),          # Pink, square, dashed
    'Spin': ('orange', 'x', ':')         # Light orange, x, dotted
}

# Locality line styles (for columns 1-3)
LOCALITY_STYLES = {
    85: '-',   # Solid
    90: '--',  # Dashed
    95: ':'    # Dotted
}

# Contention line styles (for column 4)
CONTENTION_STYLES = {
    'high': '-',     # Solid (20 keys)
    'medium': '--',  # Dashed (100 keys)
    'low': ':'       # Dotted (1000 keys)
}

def generate_synthetic_throughput(system, num_threads, num_nodes, contention, locality):
    """
    Generate synthetic throughput data based on the paper's findings.
    """
    total_threads = num_threads * num_nodes
    
    if system == 'ALock':
        base_throughput = 500000
        thread_factor = 1.0 + (num_threads - 1) * 0.15
        locality_factor = 1.0 + (locality - 85) * 0.02 if locality < 100 else 1.3
        if contention == 'high':
            contention_factor = 1.2
        elif contention == 'medium':
            contention_factor = 1.0
        else:
            contention_factor = 0.85
        
        if total_threads > 100:
            degradation = 1.0 - (total_threads - 100) * 0.001
        else:
            degradation = 1.0
        
        throughput = base_throughput * thread_factor * locality_factor * contention_factor * degradation
        
    elif system == 'MCS':
        base_throughput = 200000
        thread_factor = 1.0 + (num_threads - 1) * 0.12
        locality_factor = 1.0 + (locality - 85) * 0.01 if locality < 100 else 0.1  # Very low for 100% local
        if contention == 'high':
            contention_factor = 0.6
        elif contention == 'medium':
            contention_factor = 0.9
        else:
            contention_factor = 1.0
        
        if total_threads > 80:
            degradation = 1.0 - (total_threads - 80) * 0.002
        else:
            degradation = 1.0
        
        throughput = base_throughput * thread_factor * locality_factor * contention_factor * degradation
        
    else:  # Spin
        base_throughput = 150000
        thread_factor = 1.0 + (num_threads - 1) * 0.08
        locality_factor = 1.0 + (locality - 85) * 0.005 if locality < 100 else 0.05  # Very low for 100% local
        if contention == 'high':
            contention_factor = 0.4
        elif contention == 'medium':
            contention_factor = 0.7
        else:
            contention_factor = 0.9
        
        if total_threads > 40:
            degradation = 1.0 - (total_threads - 40) * 0.003
        else:
            degradation = 1.0
        
        throughput = base_throughput * thread_factor * locality_factor * contention_factor * degradation
    
    # Add realistic noise
    noise = np.random.normal(1.0, 0.05)
    throughput = max(0, throughput * noise)
    
    return throughput

def create_subplot_cols1_3(ax, num_nodes, contention):
    """
    Create subplot for columns 1-3 (20, 100, 1000 keys with locality variations).
    Shows 3 systems × 3 locality levels = 9 lines.
    """
    for system in SYSTEMS:
        color, marker, _ = SYSTEM_STYLE_COLS1_3[system]
        
        for locality in LOCALITY_PERCENTAGES:
            threads_list = []
            throughput_list = []
            
            for num_threads in THREADS_PER_NODE:
                throughput = generate_synthetic_throughput(
                    system, num_threads, num_nodes, contention, locality
                )
                threads_list.append(num_threads)
                throughput_list.append(throughput)
            
            linestyle = LOCALITY_STYLES[locality]
            label = f'{system} {locality}%' if system == SYSTEMS[0] else None
            
            # Set marker based on linestyle: dotted='s', dashed='x', solid=original
            if linestyle == ':':  # Dotted line
                plot_marker = 's'  # Square
                marker_edgewidth = 1
            elif linestyle == '--':  # Dashed line
                plot_marker = 'x'  # X
                marker_edgewidth = 2  # Bold X markers
            else:  # Solid line
                plot_marker = marker  # Keep original marker
                marker_edgewidth = 1
            
            # Match advisor's style: thicker lines, larger markers
            ax.plot(
                threads_list,
                throughput_list,
                color=color,
                marker=plot_marker,
                linestyle=linestyle,
                linewidth=2,  # Thicker lines like advisor's style
                markersize=6,  # Larger markers
                markeredgewidth=marker_edgewidth,
                label=label
            )
    
    ax.set_xlabel('Threads per Node', fontsize=10)
    ax.set_ylabel('Throughput (ops/s)', fontsize=10, labelpad=15)  # Add padding to prevent overlap
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(left=0, right=12)
    ax.set_ylim(bottom=0)
    ax.set_xticks([0, 4, 8, 12])  # Show major ticks, but plot all 12 points
    
    # Match advisor's style: adjust tick parameters
    ax.tick_params(axis='both', which='major', labelsize=9)
    
    return ax

def create_subplot_col4(ax, num_nodes):
    """
    Create subplot for column 4 (100% Local with contention variations).
    Shows 3 systems × 3 contention levels = 9 lines.
    """
    for system in SYSTEMS:
        color, marker, _ = SYSTEM_STYLE_COL4[system]
        
        for contention in ['high', 'medium', 'low']:
            threads_list = []
            throughput_list = []
            
            for num_threads in THREADS_PER_NODE:
                throughput = generate_synthetic_throughput(
                    system, num_threads, num_nodes, contention, 100  # 100% local
                )
                threads_list.append(num_threads)
                throughput_list.append(throughput)
            
            linestyle = CONTENTION_STYLES[contention]
            label = f'{system} {CONTENTION_LEVELS[contention]}' if system == SYSTEMS[0] else None
            
            # Set marker based on linestyle: dotted='s', dashed='x', solid=original
            if linestyle == ':':  # Dotted line
                plot_marker = 's'  # Square
                marker_edgewidth = 1
            elif linestyle == '--':  # Dashed line
                plot_marker = 'x'  # X
                marker_edgewidth = 2  # Bold X markers
            else:  # Solid line
                plot_marker = marker  # Keep original marker
                marker_edgewidth = 1
            
            # Match advisor's style: thicker lines, larger markers
            ax.plot(
                threads_list,
                throughput_list,
                color=color,
                marker=plot_marker,
                linestyle=linestyle,
                linewidth=2,  # Thicker lines like advisor's style
                markersize=6,  # Larger markers
                markeredgewidth=marker_edgewidth,
                label=label
            )
    
    ax.set_xlabel('Threads per Node', fontsize=10)
    ax.set_ylabel('Throughput (ops/s)', fontsize=10, labelpad=15)  # Add padding to prevent overlap
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(left=0, right=12)
    ax.set_ylim(bottom=0)
    ax.set_xticks([0, 4, 8, 12])  # Show major ticks, but plot all 12 points
    
    # Match advisor's style: adjust tick parameters
    ax.tick_params(axis='both', which='major', labelsize=9)
    
    return ax

def create_figure5_grid():
    """
    Create the complete Figure 5 grid layout (3x4 = 12 subplots).
    """
    fig, axes = plt.subplots(3, 4, figsize=GRID_DIMENSIONS)
    
    # Subplot labels
    labels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)', '(g)', '(h)', '(i)', '(j)', '(k)', '(l)']
    label_idx = 0
    
    # Column titles
    col_titles = ['20 Keys', '100 Keys', '1000 Keys', '100% Local']
    
    # Row titles (will be added as y-labels on leftmost plots)
    row_titles = ['5 Nodes', '10 Nodes', '20 Nodes']
    
    # Create each subplot - Columns = contention, Rows = nodes (3 plots per column)
    # Structure: 3 rows (5, 10, 20 nodes) × 4 columns (20 Keys, 100 Keys, 1000 Keys, 100% Local)
    for col_idx in range(4):
        for row_idx, num_nodes in enumerate(NUM_NODES):
            ax = axes[row_idx, col_idx]  # row_idx = 0,1,2 (3 rows), col_idx = 0,1,2,3 (4 columns)
            
            if col_idx < 3:  # Columns 1-3: contention with locality variations
                contention = ['high', 'medium', 'low'][col_idx]
                create_subplot_cols1_3(ax, num_nodes, contention)
            else:  # Column 4: 100% Local with contention variations
                create_subplot_col4(ax, num_nodes)
            
            # Only show Y-axis label on leftmost column to avoid overlap
            if col_idx > 0:
                ax.set_ylabel('')  # Remove Y-axis label for non-leftmost columns
            
            # Add subplot label
            ax.text(0.02, 0.98, labels[label_idx], transform=ax.transAxes,
                   fontsize=12, fontweight='bold', verticalalignment='top')
            label_idx += 1
            
            # Add titles at top of each plot: "20 Keys, 5 Nodes" format
            ax.set_title(f'{col_titles[col_idx]}, {row_titles[row_idx]}', 
                       fontsize=11, fontweight='bold', pad=10)
    
    # No overall title (removed as requested)
    # Add extra padding to prevent label overlap (matching advisor's style)
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98], pad=2.0)
    save_path = os.path.join('fig5_plots', 'figure5_grid.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.close()
    
    return save_path

def main():
    """
    Generate Figure 5 as a grid layout.
    """
    print("Generating Figure 5 grid layout...")
    print("=" * 60)
    
    try:
        with tqdm(total=1, desc="Creating grid", unit="figure") as pbar:
            save_path = create_figure5_grid()
            pbar.update(1)
        
        print("\n" + "=" * 60)
        print(f"✓ Successfully generated Figure 5 grid: {save_path}")
        print("\nNote: This uses synthetic data. Replace generate_synthetic_throughput() with your real data!")
        
    except Exception as e:
        print(f"\n❌ Error generating plot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)
    main()
