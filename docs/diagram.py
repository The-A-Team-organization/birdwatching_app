from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom

from diagrams.onprem.ci import Jenkins
from diagrams.onprem.iac import Ansible

from diagrams.generic.os import Ubuntu

from diagrams.programming.language import Python
from diagrams.onprem.database import Postgresql
from diagrams.onprem.network import Nginx
from diagrams.onprem.network import Consul
from diagrams.onprem.client import User, Client

diagram_attr = {"fontsize": "45", "splines": "ortho", "rankdir": "TB"}
vpc_attr = {"fontsize": "30", "bgcolor": "white", "splines": "spline"}
vm_attr = {"fontsize": "30", "bgcolor": "#E0F7FA", "splines": "spline"}
legend_attr = {
    "fontsize": "25",
    "bgcolor": "transparent",
    "style": "dashed",
    "penwidth": "2.0",
}

main_edge_attr = {"minlen": "2.0", "penwidth": "3.0", "concentrate": "true"}

with Diagram(
    "Birdwatching Infrastructure",
    filename="birdwatching_diagram",
    show=False,
    graph_attr=diagram_attr,
    edge_attr=main_edge_attr,
):
    user = User("End User")

    with Cluster("Local Environment"):
        vagrant = Custom("Vagrant", "./img/vagrant.jpg")
        virtualbox = Custom("VirtualBox", "./img/virtualbox.png")

        with Cluster("Birdwatching VMs (Vagrant on VirtualBox)", graph_attr=vpc_attr):
            with Cluster("VM5: Jenkins + Ansible", graph_attr=vm_attr):
                jenkins = Jenkins("Jenkins")
                ansible = Ansible("Ansible")

            with Cluster("VM6: Consul", graph_attr=vm_attr):
                consul = Consul("Consul")

            with Cluster("VM1: Web Server 1", graph_attr=vm_attr):
                ubuntu1 = Ubuntu("Ubuntu")
                flask1 = Python("Flask App")
                nginx1 = Nginx("Nginx Proxy")

            with Cluster("VM2: Web Server 2", graph_attr=vm_attr):
                ubuntu2 = Ubuntu("Ubuntu")
                flask2 = Python("Flask App")
                nginx2 = Nginx("Nginx Proxy")

            with Cluster("VM3: Database", graph_attr=vm_attr):
                db = Postgresql("PostgreSQL")

            with Cluster("VM4: Load Balancer", graph_attr=vm_attr):
                lb = Nginx("Nginx LB")

    user >> Edge(label="HTTP Requests", color="darkgreen") >> lb

    for n in [nginx1, nginx2]:
        lb >> Edge(label="Route Traffic", color="darkgreen") >> n

    for n, f in zip([nginx1, nginx2], [flask1, flask2]):
        n >> Edge(label="Serve App", color="darkgreen") >> f

    for f in [flask1, flask2]:
        f >> Edge(label="DB Queries", color="darkgreen") >> db

    vagrant >> Edge(label="Provision VMs", color="black") >> virtualbox
    jenkins >> Edge(label="Trigger Playbooks", color="red") >> ansible

    for node in [nginx1, flask1, nginx2, flask2, db, lb]:
        ansible >> Edge(label="Configure", color="black") >> node

    with Cluster("Legend", graph_attr=legend_attr):
        (
            Custom("", "./img/null.png")
            >> Edge(label="Provision/Configure", color="black")
            >> Custom("", "./img/null.png")
        )
        (
            Custom("", "./img/null.png")
            >> Edge(label="User Traffic", color="darkgreen")
            >> Custom("", "./img/null.png")
        )
        (
            Custom("", "./img/null.png")
            >> Edge(label="Trigger CI/CD", color="red")
            >> Custom("", "./img/null.png")
        )
