using PowerModelsDistribution
using PowerModels
using Ipopt
using JuMP
using DataFrames
using CSV


PowerModels.logger_config!("error")

include("post_flex_model_new.jl")

data_filename = "data/123Bus_GMLC/IEEE123Master.dss"
data = PowerModelsDistribution.parse_file(data_filename)
filename = "data/ADC_Placement_by_Voltage_Drop.csv"
# filename_flex = "data/ieee123_flex.csv"

filename_flex = ARGS[1]
# data_new = data_surgery(data,filename)
data_new = data_surgery(data, filename, filename_flex)
# result = run_ac_tp_opf_lm(data, with_optimizer(Ipopt.Optimizer))

# model = PowerModels.build_model(data,ACPPowerModel,post_tp_opf_lm_mod)
# result = PowerModels.optimize_model!(model,with_optimizer(Ipopt.Optimizer))
# result_old = _PMs.run_model(data, ACPPowerModel, with_optimizer(Ipopt.Optimizer), post_tp_opf_lm_mod; multiconductor=true, ref_extensions=[ref_add_arcs_trans!])

pm_new = _PMs.build_model(data_new, ACPPowerModel, post_tp_opf_lm_mod; multiconductor=true, ref_extensions=[ref_add_arcs_trans!])
result_new = _PMs.optimize_model!(pm_new, with_optimizer(Ipopt.Optimizer))

ADC = build_ADC_list(filename)
ADC_pm = convert_ADC_pm(data,ADC)
pm_to_source, source_to_pm = build_bus_renaming_dict(data_new)
bus_loads = build_bus_loads(data_new)


to_write = Dict{String,Array{Float64,1}}()
for adc in keys(ADC)
    if !(adc in keys(source_to_pm))
        continue
    end
    # @show adc
    adc_pm = source_to_pm[adc]
    load = bus_loads[adc_pm][1]
    load_id = parse(Int64,load)
    p = zeros(3)
    q = zeros(3)
    for i=1:3
        p[i] = JuMP.value(PowerModels.var(pm_new, 0, i, :pd)[load_id])*1e5
        q[i] = JuMP.value(PowerModels.var(pm_new, 0, i, :qd)[load_id])*1e5
    end
    to_write[adc] = [sum(p),sum(q)]
end

df = DataFrame(ADC = Int[], P = Float64[], Q = Float64[])
for (adc, setpoint) in to_write
    push!(df, Dict(:ADC => parse(Int64,adc), :P => setpoint[1], :Q => setpoint[2]) ) # [parse(Int64,adc), parse)Float64,setpoint[1]), parse(Float64,setpoint[2])])
end


CSV.write("PFO_output.csv", df)
