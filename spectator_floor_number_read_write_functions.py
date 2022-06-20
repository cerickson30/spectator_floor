def Glabel(G):
    """
    Returns the graph6_string of the canonical labeling of graph G using the sage algorithm
    to determine the canonical labeling.
    
    :param G: A graph object.
    """
    return G.canonical_label(algorithm='sage')().graph6_string()


##########################################################################################
#################################### Seen Dict ###########################################
##########################################################################################

def get_last_seen_dict_numbers(path_prefix='data'):
    """
    Returns the number of vertices and number of edges of the last successfully processed graph by 
    reading the names of the files in which the sets of graph6_strings of graphs whose spectator minor 
    floor number has been calculated in order to identify the number of vertices and edges in the last 
    graph whose spectator minor floor number was successfully calculated and saved to file.
    
    This is used to bound the loop that is used to rebuild the dictionary of all graphs whose spectator
    minor floor number has been calculated from the files partitioned by number of vertices and edges.
    
    :param path_prefix: The directory in which to find the partitioned files that can be used to rebuild
            the dictionary of graphs whose spectator minor floor number has been calculated.
            By default, saves these files in a directory called 'data'
    """
    import os
    
    files_list = os.listdir(path_prefix + '/seen_dict')
    max_n = 0
    for filename in files_list:
        if '_verts_' in filename:
            start_idx = filename.find('_dict_') + len('_dict_')
            stop_idx = filename.find('_verts_')
            if int(filename[start_idx:stop_idx]) > max_n:
                max_n = int(filename[start_idx:stop_idx])

    edges = max_n*(max_n - 1) // 2
    for filename in files_list:
        if f'_{max_n}_verts' in filename:
            start_idx = filename.find('_verts_') + len('_verts_')
            try:
                stop_idx = filename.index('_edges-backup.txt')
            except ValueError:
                stop_idx = filename.index('_edges.txt')
            if int(filename[start_idx:stop_idx]) < edges:
                edges = int(filename[start_idx:stop_idx])

    return (max_n, edges)



def read_partial_seen_dict(num_verts, num_edges, path_prefix='data'):
    """
    Reads a file (or backup) containing a set of graph6_strings of graphs on num_verts vertices 
    and num_edges edges whose spectator minor floor number has been calculated and saved.
    
    :param num_verts: The number of vertices that each graph listed in the file contains.
    
    :param num_edges: The number of edges that each graph listed in the file contains.
    
    :param path_prefix: The directory in which to find the partitioned files that can be used to rebuild
            the dictionary of graphs whose spectator minor floor number has been calculated.
            By default, reads looks for these files in a directory called 'data'
    """
    try:
        # Try the primary file
        with open(f'{path_prefix}/seen_dict/seen_dict_{num_verts}_verts_{num_edges}_edges.txt', 'r') as infile:
            return eval(infile.read())
    except:
        # If primary file is corrupted (empty), try backup
        with open(f'{path_prefix}/seen_dict/seen_dict_{num_verts}_verts_{num_edges}_edges-backup.txt', 'r') as infile:
            return eval(infile.read())
        
        
def write_partial_seen_dict(num_verts, num_edges, seen_dict, path_prefix='data'):
    """
    Writes a file (and backup) containing a set of graph6_strings of graphs on num_verts vertices
    and num_edges edges whose spectator minor floor number has been calculated and saved.
    
    :param num_verts: The number of vertices that each graph listed in the file contains.
    
    :param num_edges: The number of edges that each graph listed in the file contains.
    
    :param seen_dict: A nested dictionary that contains lists of graphs whose spectator minor floor
            number has been calculated.
    
    :param path_prefix: The directory in which to save the partitioned files that can be used to rebuild
            the dictionary of graphs whose spectator minor floor number has been calculated.
            By default, saves these files in a directory called 'data'
    """
    with open(f'{path_prefix}/seen_dict/seen_dict_{num_verts}_verts_{num_edges}_edges.txt', 'w') as outfile:
        outfile.write(str(seen_dict[f'{num_verts}_verts'][f'{num_edges}_edges']))
    
    # In case there's an interuption while the connection is open, make a backup
    with open(f'{path_prefix}/seen_dict/seen_dict_{num_verts}_verts_{num_edges}_edges-backup.txt', 'w') as outfile:
        outfile.write(str(seen_dict[f'{num_verts}_verts'][f'{num_edges}_edges'])) 
        

def init_seen_dict(path_prefix='data'):
    """
    Returns the nested dictionary containing lists of graph6_strings of graphs whose spectator minor
    floor number has been calculated and saved after rebuilding this dictionary from the partitioned
    files read by the read_partial_seen_dict() function.
    
    The outer dictionary has keys of the form '4_verts' and the value associated with that key is a
    dictionary whose keys are of the form '5_edges'. The value associated with seen_dict['4_verts']['5_edges']
    is a set of graph6_strings of graphs on 4 vertices and 5 edges whose spectator minor floor number 
    has been calculated and saved to a file.
    
    :param path_prefix: The directory in which to find the partitioned files that can be used to rebuild
            the dictionary of graphs whose spectator minor floor number has been calculated.
            By default, reads looks for these files in a directory called 'data'
    """
    max_n, edcount = get_last_seen_dict_numbers(path_prefix)

    vertex_keys = [f'{nn}_verts' for nn in range(11)]
    seen_dict = dict(zip(vertex_keys, [{} for nn in range(11)]))
    for nn in range(11):
        edge_dict_keys = [f"{ee}_edges" for ee in range(Integer((nn*(nn-1))/2), 0, -1)]
        seen_dict[f"{nn}_verts"] = dict(zip(edge_dict_keys,[set() for ee in range(len(edge_dict_keys))]))

    # add the graph on 0 vertices
    seen_dict['0_verts']['0_edges'] = set(Glabel(Graph(0)))
    # add the graph on 1 vertex
    seen_dict['1_verts']['0_edges'] = set(Glabel(Graph(1)))
    
    if max_n >= 2:
        # add lower vertex number graphs
        for n_verts in range(2, max_n):
            for m_edges in range(n_verts*(n_verts-1)//2, 0, -1):
                seen_dict[f'{n_verts}_verts'][f'{m_edges}_edges'] = read_partial_seen_dict(n_verts, m_edges, path_prefix)

        # add previously computed for max_n
        for m_edges in range(max_n*(max_n-1)//2, edcount-1, -1):
            seen_dict[f'{max_n}_verts'][f'{m_edges}_edges'] = read_partial_seen_dict(max_n, m_edges, path_prefix)
    
    return seen_dict



##########################################################################################
################################ Completed Dict ##########################################
##########################################################################################

def get_last_completed_dict_numbers(path_prefix='data'):
    """
    Returns the number of vertices and number of edges of the last successfully processed graph by reading
    the names of the files in which the lists of graph6_strings of graphs that have been checked for minor 
    minimality with respect to the spectator minor floor number in order to identify the number of vertices
    and edges in the last graph whose potential minor minimality was successfully checked.
    
    This is used to bound the loop that is used to rebuild the dictionary of all graphs whose 
    potential minor minimality has been checked from the files partitioned by number of vertices and edges.
    
    :param path_prefix: The directory in which to find the partitioned files that can be used to rebuild
            the dictionary of graphs whose spectator minor floor number has been calculated.
            By default, saves these files in a directory called 'data'
    """
    import os
    
    files_list = os.listdir(path_prefix + '/completed_dict')
    max_n = 0
    for filename in files_list:
        if '_verts_' in filename:
            start_idx = filename.find('_dict_') + len('_dict_')
            stop_idx = filename.find('_verts_')
            if int(filename[start_idx:stop_idx]) > max_n:
                max_n = int(filename[start_idx:stop_idx])

    edges = max_n*(max_n - 1) // 2
    for filename in files_list:
        if f'_{max_n}_verts' in filename:
            start_idx = filename.find('_verts_') + len('_verts_')
            try:
                stop_idx = filename.index('_edges-backup.txt')
            except ValueError:
                stop_idx = filename.index('_edges.txt')
            if int(filename[start_idx:stop_idx]) < edges:
                edges = int(filename[start_idx:stop_idx])

    return (max_n, edges)


## Read partial seen_dict for a given number of vertices and edges
def read_partial_completed_dict(num_verts, num_edges, path_prefix='data'):
    """
    Reads a file (or backup) containing a set of graph6_strings of graphs on num_verts vertices 
    and num_edges edges that have had their potential minor minimality with respect to the spectator
    minor floor number checked.
    
    :param num_verts: The number of vertices that each graph listed in the file contains.
    
    :param num_edges: The number of edges that each graph listed in the file contains.
    
    :param path_prefix: The directory in which to find the partitioned files that can be used to rebuild
            the dictionary of graphs whose spectator minor floor number has been calculated.
            By default, reads looks for these files in a directory called 'data'
    """
    try:
        # try the primary file
        with open(f'{path_prefix}/completed_dict/completed_dict_{num_verts}_verts_{num_edges}_edges.txt', 'r') as infile:
            return eval(infile.read())
    except:
        # If primary file is corrupted (empty), try backup
        with open(f'{path_prefix}/completed_dict/completed_dict_{num_verts}_verts_{num_edges}_edges-backup.txt', 'r') as infile:
            return eval(infile.read())
        
        
def write_partial_completed_dict(num_verts, num_edges, completed_dict, path_prefix='data'):
    """
    Writes a file (and backup) containing a set of graph6_strings of graphs on num_verts vertices 
    and num_edges edges that have had their potential minor minimality with respect to the spectator
    minor floor number checked.
    
    :param num_verts: The number of vertices that each graph listed in the file contains.
    
    :param num_edges: The number of edges that each graph listed in the file contains.
    
    :param completed_dict: A nested dictionary that contains lists of graphs that have been checked for
            minor minimality.
    
    :param path_prefix: The directory in which to save the partitioned files that can be used to rebuild
            the dictionary of graphs whose spectator minor floor number has been calculated.
            By default, saves these files in a directory called 'data'
    """
    with open(f'{path_prefix}/completed_dict/completed_dict_{num_verts}_verts_{num_edges}_edges.txt', 'w') as outfile:
        outfile.write(str(completed_dict[f'{num_verts}_verts'][f'{num_edges}_edges']))
    
    # Just in case there's an interuption while the connection is open, make a backup
    with open(f'{path_prefix}/completed_dict/completed_dict_{num_verts}_verts_{num_edges}_edges-backup.txt', 'w') as outfile:
        outfile.write(str(completed_dict[f'{num_verts}_verts'][f'{num_edges}_edges'])) 
        

def init_completed_dict(path_prefix='data'):
    """
    Returns the nested dictionary containing lists of graph6_strings of graphs that have been checked 
    for minor minimality with respect to the spectator minor floor number after rebuilding this dictionary 
    from the partitioned files read by the read_partial_completed_dict() function.
    
    The outer dictionary has keys of the form '4_verts' and the value associated with that key is a
    dictionary whose keys are of the form '5_edges'. The value associated with 
    completed_dict['4_verts']['5_edges'] is a set of graph6_strings of graphs on 4 vertices and 5 edges 
    that have been checked for minor minimality.
    
    :param path_prefix: The directory in which to find the partitioned files that can be used to rebuild
            the dictionary of graphs that have been checked for minor minimality. By default, reads looks
            for these files in a directory called 'data'
    """
    max_n, edcount = get_last_completed_dict_numbers(path_prefix)

    vertex_keys = [f'{nn}_verts' for nn in range(11)]
    completed_dict = dict(zip(vertex_keys, [{} for nn in range(11)]))
    for nn in range(11):
        edge_dict_keys = [f"{ee}_edges" for ee in range(Integer((nn*(nn-1))/2), 0, -1)]
        completed_dict[f"{nn}_verts"] = dict(zip(edge_dict_keys,[set() for ee in range(len(edge_dict_keys))]))

    # add the graph on 0 vertices
    completed_dict['0_verts']['0_edges'] = set(Glabel(Graph(0)))
    # add the graph on 1 vertex
    completed_dict['1_verts']['0_edges'] = set(Glabel(Graph(1)))
    
    if max_n >= 2:
        # add lower vertex number graphs
        for n_verts in range(2, max_n):
            for m_edges in range(n_verts*(n_verts-1)//2, 0, -1):
                completed_dict[f'{n_verts}_verts'][f'{m_edges}_edges'] = read_partial_completed_dict(n_verts, m_edges, path_prefix)

        # add previously computed for max_n
        for m_edges in range(max_n*(max_n-1)//2, edcount-1, -1):
            completed_dict[f'{max_n}_verts'][f'{m_edges}_edges'] = read_partial_completed_dict(max_n, m_edges, path_prefix)
    
    return completed_dict



##########################################################################################
################################ Minimals Dict ###########################################
##########################################################################################

def get_last_minimals_dict_numbers(path_prefix='data'):
    """
    Returns the number of vertices and number of edges of the last successfully processed graph by reading
    the names of the files containing the dictionary of graph6_strings of graphs that have been determined
    to be minor minimal with respect to the spectator minor floor number in order to identify the number
    of vertices and edges in the last graph successfully classified.
    
    This is used to read the most recent minor minimal dictionary.
    
    :param path_prefix: The directory in which to find the files containing the dictionary of minor
            minimal graphs. By default, saves these files in a directory called 'data'
    """
    import os
    
    files_list = os.listdir(path_prefix + '/minimals_dict')
    max_n = 0
    for filename in files_list:
        if '_verts_' in filename:
            start_idx = filename.find('_dict_') + len('_dict_')
            stop_idx = filename.find('_verts_')
            if int(filename[start_idx:stop_idx]) > max_n:
                max_n = int(filename[start_idx:stop_idx])

    edges = max_n*(max_n - 1) // 2
    for filename in files_list:
        if f'_{max_n}_verts' in filename:
            start_idx = filename.find('_verts_') + len('_verts_')
            try:
                stop_idx = filename.index('_edges-backup.txt')
            except ValueError:
                stop_idx = filename.index('_edges.txt')
            if int(filename[start_idx:stop_idx]) < edges:
                edges = int(filename[start_idx:stop_idx])

    return (max_n, edges)


def write_minimals_dict(num_verts, num_edges, minimals_dict, path_prefix='data'):
    """
    Writes a file (and backup) containing the dictionary of graph6_strings of graphs on at most num_verts
    vertices and at least num_edges edges that have been determined to be minor minimal with respect to the
    spectator minor floor number.
    
    :param num_verts: The number of vertices that each graph listed in the file contains.
    
    :param num_edges: The number of edges that each graph listed in the file contains.
    
    :param minimals_dict: A dictionary that contains lists of graphs that have been determined to be
            minor minimal with respect to the spectator floor number. The keys are of the form 'k_spectators'
    
    :param path_prefix: The directory in which to save the file containing the dictionary of minor minimal
            graphs. By default, saves these files in a directory called 'data'
    """
    with open(path_prefix +
              f'/minimals_dict/minimals_dict_{num_verts}_verts_{num_edges}_edges-backup.txt', 'w') as outfile:
        outfile.write(str(minimals_dict))
    
    # Just in case there's an interuption while the connection is open, make a backup
    with open(path_prefix +
              f'/minimals_dict/minimals_dict_{num_verts}_verts_{num_edges}_edges.txt', 'w') as outfile:
        outfile.write(str(minimals_dict))


def read_minimals_dict(path_prefix='data'):
    """
    Reads the saved dictionary containing the graphs determined to be minor minimal with respect to
    the spectator minor floor number.
    
    Returns a dictionary that contains lists of graphs that have been determined to be minor minimal
    with respect to the spectator floor number. The keys are of the form 'k_spectators'
    
    :param path_prefix: The directory in which the file containing the dictionary of minor minimal
            graphs is saved. By default, these files are in a directory called 'data'
    """
    max_n, edge_count = get_last_minimals_dict_numbers(path_prefix)
    
    try:
        # try the primary file
        with open(path_prefix + f'/minimals_dict/minimals_dict_{num_verts}_verts_{num_edges}_edges.txt', 'r') as infile:
            return eval(infile.read())
    except:
        # If primary file is corrupted (empty), try backup
        try:
            with open(path_prefix + f'/minimals_dict/minimals_dict_{num_verts}_verts_{num_edges}_edges-backup.txt', 'r') as infile:
                return eval(infile.read())
        except:
            # If both seen_dict.txt and seen_dict_backup.txt are corrupted, or don't exist, initialize uspcm_dict
            minimals_dict_keys = [f'{kk}_spectators' for kk in range(10)]
            minimals_dict = dict(zip(minimals_dict_keys, [set() for kk in range(10)]))
            minimals_dict['0_spectators'].add('@')
            
            return minimals_dict        



##########################################################################################
################################### USPCM Dict ###########################################
##########################################################################################

def get_last_uspcm_dict_numbers(path_prefix='data'):
    """
    Returns the number of vertices and number of edges of the last successfully processed graph by reading
    the names of the files in which the dictionary of graphs whose spectator minor floor number has been 
    calculated in order to identify the number of vertices and edges in the last graph whose spectator 
    minor floor number was successfully calculated and saved to file.
    
    This is used to bound the loop that is used to rebuild the dictionary of all graphs whose spectator
    minor floor number has been calculated from the files partitioned by number of vertices and edges.
    
    :param path_prefix: The directory in which to find the partitioned files that can be used to rebuild
            the dictionary of graphs whose spectator minor floor number has been calculated.
            By default, saves these files in a directory called 'data'
    """
    import os
    
    files_list = os.listdir(path_prefix + '/uspcm_dict')
    max_n = 0
    for filename in files_list:
        if '_verts_' in filename:
            start_idx = filename.find('_dict_') + len('_dict_')
            stop_idx = filename.find('_verts_')
            if int(filename[start_idx:stop_idx]) > max_n:
                max_n = int(filename[start_idx:stop_idx])

    edges = max_n*(max_n - 1) // 2
    for filename in files_list:
        if f'_{max_n}_verts' in filename:
            start_idx = filename.find('_verts_') + len('_verts_')
            try:
                stop_idx = filename.index('_edges-backup.txt')
            except ValueError:
                stop_idx = filename.index('_edges.txt')
            if int(filename[start_idx:stop_idx]) < edges:
                edges = int(filename[start_idx:stop_idx])

    return (max_n, edges)
        
        
## Read partial uspcm_dict for a given number of vertices and edges
def read_partial_uspcm_dict(num_verts, num_edges, path_prefix='data'):
    """
    Reads a file (or backup) containing a dictionary whose keys are graph6_strings of graphs on num_verts 
    vertices and num_edges edges whose spectator minor floor number has been calculated and whose values
    are the associated spectator minor floor number.
    
    :param num_verts: The number of vertices that each graph listed in the file contains.
    
    :param num_edges: The number of edges that each graph listed in the file contains.
    
    :param path_prefix: The directory in which to find the partitioned files that can be used to rebuild
            the dictionary of graphs whose spectator minor floor number has been calculated.
            By default, reads looks for these files in a directory called 'data'
    """
    try:
        # try the primary file
        with open(f'{path_prefix}/uspcm_dict/uspcm_dict_{num_verts}_verts_{num_edges}_edges.txt', 'r') as infile:
            return eval(infile.read())
    except:
        # If primary file is corrupted (empty), try backup
        with open(f'{path_prefix}/uspcm_dict/uspcm_dict_{num_verts}_verts_{num_edges}_edges-backup.txt', 'r') as infile:
            return eval(infile.read())
        
        
def write_partial_uspcm_dict(num_verts, num_edges, uspcm_dict, path_prefix='data'):
    """
    Writes a file (and backup) containing a dictionary of graphs on num_verts vertices and num_edges edges
    that have had their spectator minor floor number calculated. The keys in the dictionary are graph6_strings 
    and the associated value is the spectator minor floor number of the graph with that graph6_string.
    
    :param num_verts: The number of vertices that each graph listed in the file contains.
    
    :param num_edges: The number of edges that each graph listed in the file contains.
    
    :param uspcm_dict: A dictionary whose keys are graph6_strings of graphs on num_verts vertices and
            num_edges edges and the associated value is the spectator minor floor number of the graph with that
            graph6_string.
    
    :param path_prefix: The directory in which to save the partitioned files that can be used to rebuild
            the dictionary of graphs and their spectator minor floor number.
            By default, saves these files in a directory called 'data'
    """
    with open(f'{path_prefix}/uspcm_dict/uspcm_dict_{num_verts}_verts_{num_edges}_edges.txt', 'w') as outfile:
        outfile.write(str(uspcm_dict[f'{num_verts}_verts'][f'{num_edges}_edges']))
    
    # Just in case there's an interuption while the connection is open, make a backup
    with open(f'{path_prefix}/uspcm_dict/uspcm_dict_{num_verts}_verts_{num_edges}_edges-backup.txt', 'w') as outfile:
        outfile.write(str(uspcm_dict[f'{num_verts}_verts'][f'{num_edges}_edges']))  
        
        
def init_uspcm_dict(path_prefix='data'):
    """
    Returns the nested dictionary whose innermost dictionary contains the graph6_strings and associated
    spectator minor floor number of those graphs after rebuilding this dictionary from the partitioned
    files read by the read_partial_seen_dict() function.
    
    The outer dictionary has keys of the form '4_verts' and the value associated with that key is a
    dictionary whose keys are of the form '5_edges'. The value associated with seen_dict['4_verts']['5_edges']
    is a dictionary whose keys are graph6_strings of graphs on 4 vertices and 5 edges where the value is the
    spectator minor floor number of the graph with that graph6_string.
    
    :param path_prefix: The directory in which to find the partitioned files that can be used to rebuild
            the dictionary of graphs whose spectator minor floor number has been calculated.
            By default, reads looks for these files in a directory called 'data'
    """
    max_n, edcount = get_last_uspcm_dict_numbers(path_prefix)

    vertex_keys = [f'{nn}_verts' for nn in range(11)]
    uspcm_dict = dict(zip(vertex_keys, [{} for nn in range(11)]))
    for nn in range(11):
        edge_dict_keys = [f'{ee}_edges' for ee in range(Integer((nn*(nn-1))/2), -1, -1)]
        uspcm_dict[f'{nn}_verts'] = dict(zip(edge_dict_keys,[{} for ee in range(len(edge_dict_keys))]))

    # add the graph on 0 vertices
    uspcm_dict['0_verts']['0_edges'] = {Glabel(Graph(0)): 0}
    # add the graph on 1 vertex
    uspcm_dict['1_verts']['0_edges'] = {Glabel(Graph(1)): 0}
    
    if max_n >= 2:
        # add lower vertex number graphs
        for n_verts in range(2, max_n):
            for m_edges in range(n_verts*(n_verts-1)//2, 0, -1):
    #             print(n_verts, m_edges)
                uspcm_dict[f'{n_verts}_verts'][f'{m_edges}_edges'] = read_partial_uspcm_dict(n_verts, m_edges, path_prefix)

        # add previously computed for max_n
        for m_edges in range(max_n*(max_n-1)//2, edcount-1, -1):
    #         print(max_n, m_edges)
            uspcm_dict[f'{max_n}_verts'][f'{m_edges}_edges'] = read_partial_uspcm_dict(max_n, m_edges, path_prefix)
    
    return uspcm_dict



##########################################################################################
############################## Initialize All Dicts ######################################
##########################################################################################

def get_spectator_number_dictionaries(path_prefix='data'):
    """
    Returns the uspcm_dict, minimals_dict, seen_dict, and completed_dict that have either been reconstructed
    from saved files or initialized if no saved files exist.
    
    uspcm_dict: Nested dictionary of the form 
            uspcm_dict[f'{nn}_verts'][f'{ee}_edges'][graph6_string] = spectator minor floor number, where 
            nn is the number of vertices, ee is the number of edges, and graph6_string is the graph6_string 
            of that graph.
    
    minimals_dict: Dictionary of the form minimals_dict[f'{kk}_spectators'] = set of graphs which have
            spectator minor floor number equal to kk and which are minor minimal with respect to the spectator
            minor floor number.
            
    seen_dict: Nested dictionary of the form seen_dict[f'{nn}_verts'][f'{ee}_edges'] = a set of graph6_strings
            of graphs whose spectator minor floor number has been calculated and saved to file.
            
    completed_dict: Nested dictionary of the form completed_dict[f'{nn}_verts'][f'{ee}_edges'] = a set of 
            graph6_strings of graphs which have been determined as to whether or not they are minor minimal
            with respect to the spectator minor floor number.
    
    :param path_prefix: The directory in which to find the partitioned files that can be used to rebuild
            the dictionaries.
    """
    
    uspcm_dict = init_uspcm_dict(path_prefix)
    minimals_dict = read_minimals_dict(path_prefix)
    seen_dict = init_seen_dict(path_prefix)
    completed_dict = init_completed_dict(path_prefix)
        
    return uspcm_dict, minimals_dict, seen_dict, completed_dict