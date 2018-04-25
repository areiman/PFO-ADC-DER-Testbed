using PowerModels
using Ipopt
using DataFrames
using CSV

filename = ARGS[1]

network_data = PowerModels.parse_file(filename)
result = run_ac_opf(network_data,IpoptSolver())

gen_nums = [parse(Int64,i) for (i,gen) in result["solution"]["gen"]]
pg = [gen["pg"] for (i,gen) in result["solution"]["gen"]]
qg = [gen["qg"] for (i,gen) in result["solution"]["gen"]]

df = DataFrame()
df[:gen_num] = gen_nums
df[:active_power] = pg
df[:reactive_power] = qg

CSV.write("output.csv",df)
