def spec_floor():
    """
    Determines the minor floor of the spectator number for all graphs on nn vertices and
    edcount edges.
    """
    
    # Used for both the progress bar and controlling how often the partial_uspcm_dict and 
    # partial_seen_dict are written to files.
    one_percent = max(len(uspcm_dict[f'{nn}_verts'][f'{edcount}_edges']) // 100, 1)
    fraction_percent = max(len(uspcm_dict[f'{nn}_verts'][f'{edcount}_edges']) // 1000, 1)
    
    if fraction_percent < 500:
        save_percent = one_percent
    else:
        save_percent = fraction_percent
    
    # Used for progress bar
    num_graphs_worked = 0
    
    # Iterate over all graphs on nn vertices and edcount edges
    # amat is a graph6_string
    for amat in progressBar(uspcm_dict[f'{nn}_verts'][f'{edcount}_edges'], 
                            prefix = f"1st pass: nn={nn}, ee={edcount}:", 
                            suffix = '', length = 40):
        
        # Skip those graphs whose spectator minor floor has already been determined.
        if amat in seen_dict[f'{nn}_verts'][f'{edcount}_edges']:
            num_graphs_worked += 1
            continue
        
        # Skip the disconnected graphs since we can sum over connected components and save progress
        if Graph(amat).is_connected() == False:
            seen_dict[f'{nn}_verts'][f'{edcount}_edges'].add(amat)
            write_partial_uspcm_dict(nn, edcount, uspcm_dict, path_prefix)
            if edcount > 1:
                write_partial_uspcm_dict(nn, edcount-1, uspcm_dict, path_prefix)
            write_partial_seen_dict(nn, edcount, seen_dict, path_prefix)
            num_graphs_worked += 1
            continue
            
        # Current number that is potentially the spectator minor floor of graph amat
        mine = uspcm_dict[f'{nn}_verts'][f'{edcount}_edges'][amat]
        G = Graph(amat) # Generate the graph object whose graph6_string is amat

        # For each minor xx of G, compare the computer spectator number of xx to the newly
        # computed spectator number of G and update the claimed spectator minor floor of xx
        # if necessary
        for xx in deletions(G):
            # Note: This is actually updating the number for the minor xx
            if xx in uspcm_dict[f'{nn}_verts'][f'{edcount-1}_edges']:
                old = uspcm_dict[f'{nn}_verts'][f'{edcount-1}_edges'][xx]
                uspcm_dict[f'{nn}_verts'][f'{edcount-1}_edges'][xx] = min(mine, old)
            else:
                old = usp_comp(Graph(xx))
                uspcm_dict[f'{nn}_verts'][f'{edcount-1}_edges'][xx] = min(mine, old)
        for xx in contractions(G):
            # Note: This is actually updating the number for the minor xx
            xx_num_verts = Graph(xx).num_verts()
            xx_num_edges = Graph(xx).num_edges()
            old = uspcm_dict[f'{xx_num_verts}_verts'][f'{xx_num_edges}_edges'][xx]
            if old > mine:
                print(f'Exception found: {G.graph6_string()} has uspc {mine}', end='')
                print(f' with minor {Graph(xx).graph6_string()} of uspc {uspcm_list[-2][edplace][xx]}.')
                pass


        # Save the progress
        seen_dict[f'{nn}_verts'][f'{edcount}_edges'].add(amat)
        num_graphs_worked += 1
        # Save to file every one percent of the way through
        if num_graphs_worked % save_percent == 0:
            write_partial_uspcm_dict(nn, edcount, uspcm_dict, path_prefix)
            if edcount > 1:
                write_partial_uspcm_dict(nn, edcount-1, uspcm_dict, path_prefix)
            write_partial_seen_dict(nn, edcount, seen_dict, path_prefix)



##################################################################
###### Functions to determine minimality in the second pass ######
##################################################################

def check_minimality(G, uspcm_dict):
    """
    Uses the dictionary of graphs and their spectator minor floor numbers calculated by the spec_floor_first_pass()
    function to determine which graphs are minor minimal with respect to the spectator minor floor number.
    """

    G, g6_str = get_canonical_graph(G)
    G_spec_floor = get_spectator_floor(G, uspcm_dict)

    for H in deletions(G):
        if get_spectator_floor(H, uspcm_dict) == G_spec_floor:
            # G is not minor minimal
            return None
    for H in contractions(G):
        if get_spectator_floor(H, uspcm_dict) == G_spec_floor:
            # G is not minor minimal
            return None
    else:
        # G is minor minimal
        return (g6_str, G_spec_floor)
    
    
    
def determine_minimals(nn, num_edges, minimals_dict=None, uspcm_dict=None, completed_dict=None, save=False, path_prefix='data'):
    
    if uspcm_dict is None:
        uspcm_dict = get_full_uspcm_dict()
        
    if minimals_dict is None:
        minimals_dict_keys = [f'{kk}_spectators' for kk in range(10)]
        minimals_dict = dict(zip(minimals_dict_keys, [set() for kk in range(10)]))
        
    
    # for edge_key in uspcm_dict.get(f'{nn}_verts'):
    if save==True:
        # print(f'{nn}_verts', f'{num_edges}_edges')
        one_percent = max(len(uspcm_dict.get(f'{nn}_verts').get(f'{num_edges}_edges')) // 100, 1)
        fraction_percent = max(len(uspcm_dict.get(f'{nn}_verts').get(f'{num_edges}_edges')) // 1000, 1)

        if fraction_percent < 500:
            save_percent = one_percent
        else:
            save_percent = fraction_percent


    # num_edges = edge_key.split('_')[0]
#         print(f'Working on graphs on {nn} vertices and {num_edges} edges...')

    num_graphs_worked = 0

    for g6_str in progressBar(uspcm_dict.get(f'{nn}_verts').get(f'{num_edges}_edges'), 
                        prefix = f"2nd pass: nn={nn}, ee={num_edges}:", 
                        suffix = '', length = 40):
        if Graph(g6_str).is_connected():
#                 print(g6_str)
            result = check_minimality(g6_str, uspcm_dict)
            if result is not None:
                G_spec_num = result[1]
                minimals_dict.get(f'{G_spec_num}_spectators').add(g6_str)
                
        completed_dict.get(f'{nn}_verts').get(f'{num_edges}_edges').add(g6_str)
        num_graphs_worked += 1

        if num_graphs_worked % save_percent == 0:
            with open(path_prefix +
              f'/minimals_dict/minimals_dict_{nn}_verts_{num_edges}_edges.txt', 'w') as outfile:
                outfile.write(str(minimals_dict))
            write_partial_completed_dict(nn, num_edges, completed_dict, path_prefix)
    
    write_partial_completed_dict(nn, num_edges, completed_dict, path_prefix)
                    
    return minimals_dict, completed_dict







##############################################################################
##############################################################################
##############################################################################
##############################################################################

def get_full_uspcm_dict():
    """
    Access the GitHub repo to put together the complete uspcm_dict, the dictionary of connected graphs 
    on up to 10 vertices (inclusive) with the spectator number for each graph.

    This is a nested dictionary, to access, e.g., the dictionary of connected graphs on 6 vertices and 
    10 edges, use uspcm_dict['6_verts']['10_edges']. The innermost dictionary's keys are graph6_strings 
    and the values are the spectator number for that graph.
    """
    
    import requests

    uspcm_dict = {}
    url_path = 'https://raw.githubusercontent.com/cerickson30/qBound/main/data/uspcm_dict/'


    for num_verts in range(2):
        uspcm_dict[f'{num_verts}_verts'] = {}

        filename = f'uspcm_dict_{num_verts}_verts_{0}_edges.txt'

        file_url = f'{url_path}/{filename}'
        response = requests.get(file_url)
        uspcm_dict[f'{num_verts}_verts'][f'{0}_edges'] = eval(response.text)


    for num_verts in range(2, 11):
        uspcm_dict[f'{num_verts}_verts'] = {}

        for num_edges in range(num_verts*(num_verts-1)//2, 0, -1):
            filename = f'uspcm_dict_{num_verts}_verts_{num_edges}_edges.txt'

            file_url = f'{url_path}/{filename}'
            response = requests.get(file_url)
            uspcm_dict[f'{num_verts}_verts'][f'{num_edges}_edges'] = eval(response.text)
            
    return uspcm_dict



def get_partial_uspcm_dict(num_verts, num_edges):
    """
    Access the GitHub repo to get just the part of the uspcm_dict for num_verts vertices and num_edges
    edges, where num_verts is at most 10.

    This is a nested dictionary, to access, e.g., the dictionary of connected graphs on 6 vertices and 
    10 edges, use uspcm_dict['6_verts']['10_edges']. The innermost dictionary's keys are graph6_strings 
    and the values are the spectator number for that graph.
    
    :param num_verts: The number of vertices.
    
    :param num_edges: The number of edges.
    """
    
    import requests

    uspcm_dict = {}
    url_path = 'https://raw.githubusercontent.com/cerickson30/qBound/main/data/uspcm_dict/'
    filename = f'uspcm_dict_{num_verts}_verts_{num_edges}_edges.txt'

    file_url = f'{url_path}/{filename}'
    response = requests.get(file_url)
    
    uspcm_dict[f'{num_verts}_verts'] = {}
    uspcm_dict[f'{num_verts}_verts'][f'{num_edges}_edges'] = eval(response.text)

    return uspcm_dict



def read_minor_minimals():
    """
    Returns the dictionary of graphs which are minor minimal with respect to the spectator minor floor 
    number from the GitHub repo.
    """
    import requests
    
    url = 'https://raw.githubusercontent.com/cerickson30/qBound/main/data/minimals_dict.txt'
    response = requests.get(url)
    return eval(response.text)



def display_connected_minimal_graphs(spec_num, minimals_dict=None):
    """
    Prints the connected minor-minimal graphs with spectator number equal to spec_num.
    
    :param spec_num: The spectator minor floor number.
    
    :param minimals_dict: Optional argument. A dictionary of minor minimal graphs where the keys are 
            the spectator minor floor number and the associated value is the set of graphs which are 
            minor minimal with respect to that spectator minor floor number. If not provided, then the
            read_minor_minimals() function will be used to fetch the dictionary from the github repo.
    """
    
    if minimals_dict is None:
        minimals_dict = read_minor_minimals()
    
    if spec_num >= 5:
        num = len(minimals_dict[f'{spec_num}_spectators'])
        message = f"""Warning: There are {num} connected minor-minimal graphs on at most 10 vertices with spectator number {spec_num},
are you sure you want to proceed?
Enter 'Yes' to print all {num} of the graphs.\n"""
        response = input(message)
        if response != 'Yes':
            return None
    

    
    graph_list = list(minimals_dict[f'{spec_num}_spectators'])
    nrows = ceil(len(graph_list)/3)
    counter = 0
    while len(graph_list) > 2:

        row = [graph_list.pop(0), graph_list.pop(0), graph_list.pop(0)]
        G1 = Graph(row[0])
        G2 = Graph(row[1])
        G3 = Graph(row[2])
        counter += 3

        ga = graphics_array((G1.plot(title=row[0]), G2.plot(title=row[1]), G3.plot(title=row[2])))
        ga.show(figsize=(15,3))
        print('\n')


    if len(graph_list) == 2:
        row = [graph_list.pop(0), graph_list.pop(0)]
        G1 = Graph(row[0])
        G2 = Graph(row[1])
        counter += 2

        ga = graphics_array((G1.plot(title=row[0]), G2.plot(title=row[1])))
        ga.show(figsize=(15,3))
        print('\n')
    elif len(graph_list) == 1:
        row = [graph_list.pop(0)]
        G1 = Graph(row[0])
        counter += 1

        G1.show(title=row[0], figsize=(15,3), fontsize=14)
        print('\n')
        
        
        
def get_spectator_floor(graph, uspcm_dict=None):
    """
    Returns the spectator floor number of the given graph.
    
    :param graph: A graph, graph6_string, or adjacency matrix for a connected graph on at most 10 vertices.
    
    :param uspcm_dict: Optional argument. A dictionary of spectator floor numbers, either the complete 
            dictionary or partial dictionary with the spectator floor numbers for graphs on the number of 
            vertices and edges that the graph argument has. If not provided, the get_partial_uspcm_dict() 
            function will be used to fetch the partial dictionary from the github repo.
    """
    G, g6_str = get_canonical_graph(graph)
        
    if G.num_verts() > 10 or G.is_connected() == False:
        return "This function only works for connected graphs on at most 10 vertices"

    num_verts = G.num_verts()
    num_edges = G.num_edges()
    
    if uspcm_dict is None:
        uspcm_dict = get_partial_uspcm_dict(num_verts, num_edges)

    return uspcm_dict[f'{num_verts}_verts'][f'{num_edges}_edges'][g6_str]



def get_canonical_graph(graph):
    """
    Returns the graph and graph6_string for the canonical labelling of the graph passed into this function.
    
    :param graph: A graph object, graph6_string, or adjacency matrix for a graph.
    """
    try:
        mat = Matrix(graph)
        G = Graph(mat)
        g6_str = G.canonical_label(algorithm='sage').graph6_string()
    except TypeError:
        if type(graph) == str:
            G = Graph(graph)
            g6_str = G.canonical_label(algorithm='sage').graph6_string()
        elif type(graph) == Graph:
            G = graph
            g6_str = G.canonical_label(algorithm='sage').graph6_string()
            
    return G, g6_str

        

def has_minor(G, H):
    """
    Determines if graph H is a minor of graph G
    
    :param G: A graph object, graph6_string, or adjacency matrix for a graph.
    
    :param H: A graph object, graph6_string, or adjacency matrix for a graph.
    """
    g,_ = get_canonical_graph(G)
    h,_ = get_canonical_graph(H)
            
    try:
        m = g.minor(h)
        return True
    except:
        return False
    
    

def find_minimal_representation(graph, uspcm_dict=None, minimals_dict=None):
    """
    Determines if the graph, G, passed in as an argument is minor minimal, if G is minor minimal, then its
    graph6_string is returned. If G is not minor minimal, then the function returns the graph6_string of
    a minor of G which has the same spectator minor floor number as G and is minor minimal with respect to
    that spectator minor floor number.
    
    :param graph: A graph, graph6_string, or adjacency matrix for a connected graph on at most 10 vertices
    
    :param uspcm_dict: Optional argument. A dictionary of spectator floor numbers, either the complete 
            dictionary or partial dictionary with the spectator floor numbers for graphs on the same number 
            of vertices and edges as G. If not provided, the get_partial_uspcm_dict() function will be used 
            to fetch the partial dictionary from the github repo.
            
    :param minimals_dict: Optional argument. A dictionary of minor minimal graphs where the keys are the
            spectator minor floor number and the associated value is the set of graphs which are minor 
            minimal with respect to that spectator minor floor number. If not provided, then the
            read_minor_minimals() function will be used to fetch the dictionary from the github repo.
    """
    G, g6_str = get_canonical_graph(graph)
        
    if G.num_verts() > 10 or G.is_connected() == False:
        return "This function only works for connected graphs on at most 10 vertices"

    num_verts = G.num_verts()
    num_edges = G.num_edges()
        
    G_spec_floor = get_spectator_floor(g6_str, uspcm_dict)
    
    if minimals_dict is None:
        minimals_dict = read_minor_minimals()
    
    if g6_str in minimals_dict[f'{G_spec_floor}_spectators']:
        print(f'{graph} is minor-minimal, the canonical labelling of {graph} has graph6_string of {g6_str}')
        if type(graph) == Graph:
            graph.show(title = f'G: {g6_str}, spec_floor = {G_spec_floor}')
        else:
            G.show(title = f'G: {g6_str}, spec_floor = {G_spec_floor}')
        return g6_str
    for H_str in minimals_dict[f'{G_spec_floor}_spectators']:
        if has_minor(G, H_str):
            print(f'{H_str} is a minor of {graph}, both have spectator floor of {G_spec_floor}, so {graph} is NOT minor-minimal')
            ga = graphics_array((G.plot(title = f'G: {g6_str}, spec_floor = {G_spec_floor}'),
                                Graph(H_str).plot(title = f'H: {H_str}, spec_floor = {G_spec_floor}')))
            ga.show()
            return H_str
        
        
        
        
        
def progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    import datetime
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar(iteration):
        try:
            percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
            filledLength = int(length * iteration // total)
        except ZeroDivisionError:
            percent = 100
            filledLength = length
        
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {prefix} |{bar}| {percent}% {suffix}', end = printEnd, flush=False)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()