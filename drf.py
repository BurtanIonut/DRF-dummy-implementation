
def add_user(cluster, user_to_cluster):

    user = {}

    user["user"] = user_to_cluster
    user["allocated_cpu"] = 0
    user["allocated_ram"] = 0

    dominant_share = user["user"]["cpu"] / cluster["total_cpu"]
    if dominant_share < user["user"]["ram"] / cluster["total_ram"]:
        user["dominant_resource"] = "ram"
        user["dominant_share"] = user["user"]["ram"] / cluster["total_ram"]
    else:
        user["dominant_resource"] = "cpu"
        user["dominant_share"] = dominant_share

    user["current_dominant_share"] = 0
    user["tasks_allocated"] = 0

    return user

def initiate_cluster(cluster_cpu, cluster_ram, users):

    cluster = {}

    cluster["total_cpu"] = cluster_cpu
    cluster["total_ram"] = cluster_ram
    cluster["allocated_cpu"] = 0
    cluster["allocated_ram"] = 0
    cluster["users"] = {}

    for user in users:
        cluster["users"][user["id"]] = add_user(cluster, user)

    return cluster

def initiate_user(cpu, ram, id):

    user = {}

    user["id"] = id
    user["cpu"] = cpu
    user["ram"] = ram

    return user

def next_round(cluster):
    
    #pick minimal dominant share
    d_s = 1
    d_r = ''
    user_id = ''
    for key in cluster["users"].keys():
        if d_s > cluster["users"][key]["current_dominant_share"]:
            d_s = cluster["users"][key]["current_dominant_share"]
            d_r = cluster["users"][key]["dominant_resource"]
            user_id = key
    
    #check if allocation is possible
    if  (cluster["users"][user_id]["user"]["cpu"] + cluster["allocated_cpu"] > cluster["total_cpu"]) or \
        (cluster["users"][user_id]["user"]["ram"] + cluster["allocated_ram"] > cluster["total_ram"]):
        return 0
    else:
        #update total allocated resources of the cluster
        cluster["allocated_cpu"] += cluster["users"][user_id]["user"]["cpu"]
        cluster["allocated_ram"] += cluster["users"][user_id]["user"]["ram"]
        #update total allocated resource of the user and its dominant share as well as the number of allocated tasks
        cluster["users"][user_id]["allocated_cpu"] += cluster["users"][user_id]["user"]["cpu"]
        cluster["users"][user_id]["allocated_ram"] += cluster["users"][user_id]["user"]["ram"]
        cluster["users"][user_id]["current_dominant_share"] += cluster["users"][user_id]["dominant_share"]
        cluster["users"][user_id]["tasks_allocated"] += 1
   
    return 1

def display_cluster(cluster):
    print("Total CPU: ",cluster["total_cpu"])
    print("Total RAM: ",cluster["total_ram"])
    print("---")
    print("ALLOCATED CPU: ",cluster["allocated_cpu"],"->","{:0.2f}".format(cluster["allocated_cpu"] * 100 /cluster["total_cpu"]),"%")
    print("ALLOCATED RAM: ",cluster["allocated_ram"],"->","{:0.2f}".format(cluster["allocated_ram"] * 100 /cluster["total_ram"]),"%")
    print("---")
    for key in cluster["users"].keys():
        print("\tUser ", key, " status:")
        print("\t\tPer task CPU req: ",cluster["users"][key]["user"]["cpu"])
        print("\t\tPer task RAM req: ",cluster["users"][key]["user"]["ram"])
        print("\t\tOrig Dom share  : ","{:0.2f}".format(cluster["users"][key]["dominant_share"] * 100), "%")
        print("\t\tDominant res    : ",cluster["users"][key]["dominant_resource"])
        print("\t\tTotal CPU alloc : ",cluster["users"][key]["allocated_cpu"])
        print("\t\tTotal RAM alloc : ",cluster["users"][key]["allocated_ram"])
        print("\t\tTasks allocated : ",cluster["users"][key]["tasks_allocated"])
        #print("\t\tCrt Dom share   : ","{:0.2f}".format(cluster["users"][key]["current_dominant_share"]))
        print("---")

def display_cluster2(cluster):
    print("Total Resources")
    print("\t CPU: ",cluster["total_cpu"])
    print("\t RAM: ",cluster["total_ram"])
    print("Allocated Resources")
    print("\t CPU: ",cluster["allocated_cpu"],"->","{:0.2f}".format(cluster["allocated_cpu"] * 100 /cluster["total_cpu"]),"%")
    print("\t RAM: ",cluster["allocated_ram"],"->","{:0.2f}".format(cluster["allocated_ram"] * 100 /cluster["total_ram"]),"%")
    print("---")
    for key in cluster["users"].keys():
        print("User ", key, "Resources per task: cpu", cluster["users"][key]["user"]["cpu"], "| " "ram", cluster["users"][key]["user"]["ram"])
        print("\tDominant res    : ",cluster["users"][key]["dominant_resource"])
        print("\tTasks allocated : ",cluster["users"][key]["tasks_allocated"])
        print("\tCrt Dom share   : ","{:0.2f}".format(cluster["users"][key]["current_dominant_share"] * 100), "%")
    print("---")

def end_tasks(tasks_remove, cluster):
    flag = 0
    tasks = tasks_remove.split(' ')
    for task in tasks:
        if task == 'A':
            if cluster["users"]["A"]["tasks_allocated"] > 0:
                cluster["users"]["A"]["tasks_allocated"] -= 1
                cluster["users"]["A"]["current_dominant_share"] -=  cluster["users"]["A"]["dominant_share"]
                cluster["allocated_cpu"] -= cluster["users"]["A"]['user']["cpu"]
                cluster["allocated_ram"] -= cluster["users"]["A"]['user']["ram"]
                flag = 1
        if task == 'B':
            if cluster["users"]["B"]["tasks_allocated"] > 0:
                cluster["users"]["B"]["tasks_allocated"] -= 1
                cluster["users"]["B"]["current_dominant_share"] -=  cluster["users"]["B"]["dominant_share"]
                cluster["allocated_cpu"] -= cluster["users"]["B"]['user']["cpu"]
                cluster["allocated_ram"] -= cluster["users"]["B"]['user']["ram"]
                flag = 1
        if task == 'C':
            if cluster["users"]["C"]["tasks_allocated"] > 0:
                cluster["users"]["C"]["tasks_allocated"] -= 1
                cluster["users"]["C"]["current_dominant_share"] -=  cluster["users"]["C"]["dominant_share"]
                cluster["allocated_cpu"] -= cluster["users"]["C"]['user']["cpu"]
                cluster["allocated_ram"] -= cluster["users"]["C"]['user']["ram"]
                flag = 1
    return flag

def main():

    user_A = initiate_user(1, 6, 'A')
    user_B = initiate_user(3, 1, 'B')
    user_C = initiate_user(2, 3, 'C')

    cluster = initiate_cluster(12, 28, [user_A, user_B, user_C])
    #cluster = initiate_cluster(12, 32, [user_A, user_B])

    print("<<<INITIAL CLUSTER STATUS>>>")
    display_cluster(cluster)
    message = 'notend'
    count = 1
    flag = 0

    while message != 'end':
        if next_round(cluster) == 1:
            print("<<<ROUND: ", count, " >>>")
            display_cluster2(cluster)
            if flag == 1:
                input()
            count += 1
        else:
            print("CLUSTER FULL")
            flag = 1
            remove_tasks = input()
            if remove_tasks == 'end':
                break
            elif end_tasks(remove_tasks, cluster) == 1:
                print("<<<ROUND: ", count, " >>>")
                display_cluster2(cluster)
                count += 1
                input()

if __name__ == '__main__':
    main()