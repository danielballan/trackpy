"""Temporally global trajectory linkingafter Jaqaman et al."""

import hungarian  # TOOD import at func or class level

def confusing_outer(a, b):
    return np.sum(np.sum(np.subtract.outer(a, b)**2, -1), 1)

def generate_cost_matrix(trajectories, cutoff, costs):
    dtype = np.float64
    pos_columns = ['x', 'y']
    
    t = trajectories  # shorthand
    b = costs['initializing']
    d = costs['terminating']
    alt_b = costs['alt_initializing']
    alt_d = costs['alt_terminating']
    N = trajectories['particle'].nunique()
    print N

    start = t.groupby('particle').first()  # assuming sorted by frame; TODO check this or ensure this
    end = t.groupby('particle').last()
    gap_closing = confusing_outer(start[pos_columns], end[pos_columns])
    gap_closing = np.where(gap_closing < cutoff**2, gap_closing, np.zeros_like(gap_closing))
    
    after_end = end.frame + 1
    after_end = after_end[after_end.isin(t.frame)].values
    
    before_start = start.frame - 1
    before_start = before_start[before_start.isin(t.frame)].values
    
    merging = confusing_outer(start[pos_columns].values, t.set_index('frame').loc[after_end, pos_columns].values)  # Where were you after each traj ended? For merging.
    splitting = confusing_outer(end[pos_columns].values, t.set_index('frame').loc[before_start, pos_columns].values)  # Where were you before each traj started? For splitting.
    
    identity = np.eye(N)
    initializing = b*identity
    terminating = d*identity
    alt_initializing = alt_b*identity # TODO wrong shape
    alt_terminating = alt_d*identity  # TODO wrong shape
        
    lower_right_block = np.finfo(dtype).eps
    center_block = np.zeros((splitting.shape[0], merging.shape[1]))
    
    # Assemble pieces into big cost matrix (Jaqaman Fig. 1)
    row0 = np.hstack([gap_closing, merging, terminating])
    row1 = np.hstack([splitting, center_block, alt_terminating])
    row2 = np.hstack([initializing, alt_initializing, lower_right_block])
    cost_matrix = np.vstack([row0, row1, row2])
    
    return cost_matrix
