using PowerModels
using Ipopt
using JuMP
using DataFrames
using CSV


include("post_flex_model.jl")

filename = ARGS[1]
ADC_filename = ARGS[2]

# read data files
data = PowerModels.parse_file(filename)
flex_data = CSV.read(ADC_filename)

# number of loads
num_load = size(flex_data,1)
# dictionary contining the A and B matrices
A = Dict{Int64,Any}()
B = Dict{Int64,Any}()

# populating the A and B dictionaries
for i=1:num_load
    ca = split(flex_data[:A][i][2:end-1], '|')
    cb = split(flex_data[:b][i][2:end-1], '|')
    a = zeros(length(ca),2)
    b = zeros(length(ca))
    for j=1:length(ca)
        za = split(ca[j],' ')
        a[j,:] = parse.(Float64,za)
    end
    b = parse.(Float64,cb)
    A[i] = a
    B[i] = b
end


# build base optimization model with loads as variables
m = JuMP.Model(solver=IpoptSolver())
model, var_refs = post_ac_opf_withload(data, m, A, B)

# solver the model
status = solve(model)

# extract solution and write output.csv
gen_nums = [parse(Int64,i) for (i,gen) in data["gen"]]
pg = [getvalue(var_refs["pg"][i]) for i in gen_nums]
qg = [getvalue(var_refs["qg"][i]) for i in gen_nums]

df = DataFrame()
df[:gen_num] = gen_nums
df[:active_power] = pg
df[:reactive_power] = qg

CSV.write("output.csv",df)
