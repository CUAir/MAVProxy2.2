import numpy as np
from sda_rrt import *
import sda_pdriver
import modules.lib.mp_geometry as mp_geo

wplist = [mp_geo.Waypoint(0.0, 0.0, 584.380004883), mp_geo.Waypoint(-19.4149408731, 120.620557966, 594.37), mp_geo.Waypoint(-230.209528262, 269.171369629, 634.37), mp_geo.Waypoint(-453.482048157, 209.910688426, 644.37), mp_geo.Waypoint(-454.861825467, 71.0911618467, 639.37), mp_geo.Waypoint(256.554153409, 105.803868799, 644.37)]


'''def get_index_of_ith_perm_waypoint_after_current( i, curr_wp_index=0):
    if i < 1:
        return curr_wp_index
    if curr_wp_index + i >= len(wplist):
        return -1
    
    perm_wp_seen = 0  
    while perm_wp_seen < i and curr_wp_index < len(wplist):
        perm_wp_seen += 1
        curr_wp_index += 1
        while curr_wp_index < len(wplist) and wplist[curr_wp_index].sda == True:
            curr_wp_index += 1
    return curr_wp_index if curr_wp_index < len(wplist) else -1

# 0 is not 1 6 6 2

WAYPOINT_LOOKAHEAD_COUNT = 4
currentWPIndex = 2
for i in range(WAYPOINT_LOOKAHEAD_COUNT): 
    i = 1 

    # for all waypoints we have to do lookahead calculations for 
    if i > 0:
        last_perm_wp_index = get_index_of_ith_perm_waypoint_after_current(i - 1, currentWPIndex)
        while wplist[last_perm_wp_index].sda:
            last_perm_wp_index += 1
        plane_xyz = wplist[last_perm_wp_index].dv
        cwpi = get_index_of_ith_perm_waypoint_after_current(i, currentWPIndex)
        if cwpi == -1:
            break
        assert not wplist[cwpi].sda
        j = currentWPIndex
        k = 0
        print (k, i, j, cwpi, currentWPIndex)

        while j < cwpi:
            if not wplist[j].sda:
                k += 1
            j += 1
        print (k, i, j, cwpi, currentWPIndex)
        assert k == i, str(k) + " is not " + str(i) + ' ' + str(j) + ' ' + str(cwpi) + ' ' + str(currentWPIndex) 

'''


points = []
nns = [] 
last_added_nodes = []
point, lst, node = np.array([-474.28069748694679, 147.69480208410744, 667.28000366210938]), [RRTNode(position=np.array([167.79994472875953, 87.607068432762631, 667.28000366210938]) , heading=np.array([0.15300981988175694, -0.95228279803394966, 0.26409367199610079]) , time_stamp=30391.0423349)], RRTNode(position=np.array([167.79994472875953, 87.607068432762631, 667.28000366210938]) , heading=np.array([0.15300981988175694, -0.95228279803394966, 0.26409367199610079]) , time_stamp=30391.0423349)
points.append(point)
nns.append(lst)
last_added_nodes.append(node)


inputs = []
results = []

pdriver = sda_pdriver.ProbDriver(model=sda_pdriver.ProbModelStatic())

pdriver.add_stat_obst(mp_geo.StationaryObstacle(54, np.array([-326.784746894, 157.383587005, 1803.20001595])))
pdriver.add_stat_obst(mp_geo.StationaryObstacle(15.24, np.array([-167.047216609, 219.507556996, 1803.20001595])))
pdriver.generate_model()
test_tree = RRTree(pdriver.current_model, None, increment=5, constrain=True, min_turning_radius=40, timeout=2)


def extend_tree_sim(n, l, p):
    found_goal = False
    tree = n
    goal = p
    last_added_node = l
    i = 0
    fafa = True
    while not found_goal:
        i += 1
        # get a list of new nodes to add and the node the list should attach to
        new_node_set, nearest_tree_node = test_tree.extend_tree(tree, last_added_node, goal, [], fafa)
        fafa = False
        # If the list is empty that means we couldn't extend the tree however the extension algorithm was trying to do
        # Therefore, we just run extend tree again until it works
        if not new_node_set:
            last_added_node = nearest_tree_node
            continue
        print "new node set", len(new_node_set)
        #print "tree len", len(tree)
        # linking the new nodes to the tree
        nearest_tree_node.add_child(new_node_set[0])
        new_node_set[0].set_parent(nearest_tree_node)
        last_added_node = new_node_set[-1]
        tree += new_node_set
        # checks to see if we have found goal
        found_goal = np.linalg.norm(last_added_node.position - goal) < test_tree.increment
        if found_goal:
            # the heading on the goal node shouldn't matter... i think?
            goal_node = RRTNode(goal, last_added_node.heading, time_stamp=last_added_node.time_stamp)
            goal_node.set_parent(last_added_node)
            tree.append(goal_node)
        test_tree.write_tree(tree, 'tree.debug', goal)
    return tree


for p, n, l in zip(points, nns, last_added_nodes):


    tree = extend_tree_sim( n, l, p)
    filtered_path = filter(lambda x: x.pinned, tree)
    path = test_tree.prune(tree)
    test_tree.write_tree(tree, 'final_tree.debug', p)
    test_tree.write_tree(path, 'pruned.debug', p)
    #test_tree.write_tree(filtered_path, 'filtered.debug', p)
    #results.append(tree.constrain_movement_towards_point(p, n, l))
    
#for i, nodes, node in enumerate(results):


    
