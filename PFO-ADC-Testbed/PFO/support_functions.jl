using PowerModelsDistribution
using PowerModels
using Ipopt
using JuMP
using DataFrames
using CSV
# using Memento





# perform changes to the PowerModels data structure
function  data_surgery(data,filename,filename_flex)
    # data = PowerModelsDistribution.parse_file("IEEETestCases/123Bus_GMLC/IEEE123Master.dss")
    data_new = deepcopy(data)

    ADC = build_ADC_list(filename)
    ADC_pm = convert_ADC_pm(data,ADC)

    bus_loads = build_bus_loads(data)


    # @show buspairs = branches_to_buspairs(data,branches_to_remove)


    # change voltage bounds for buses in the adc control area
    for (adc,control_area) in ADC_pm
        # control_area_trimmed  = control_area
        control_area_trimmed = setdiff(control_area,[adc])
        for b in control_area_trimmed
            # delete!(data_new["bus"],b)
            data_new["bus"][b]["vmin"] = [-100,-100,-100]
            data_new["bus"][b]["vmax"] = [100,100,100]
        end
    end

    # increase branch limits for branches in the control area
    branches_to_remove = find_branches_to_remove(data,ADC_pm)
    for b in branches_to_remove
        # delete!(data_new["branch"],b)
        data_new["branch"][b]["rate_a"] = [100,100,100]
        data_new["branch"][b]["rate_b"] = [100,100,100]
        data_new["branch"][b]["rate_c"] = [100,100,100]
    end

    # add loads
    adc_sumloads = find_ADC_sumloads(data,ADC_pm,bus_loads)

    for adc in keys(ADC_pm)
        if adc in keys(bus_loads)
            # println("position 1")
            load = bus_loads[adc][1]
            # println("type of load connection = ", data["load"][load]["conn"])
            # println("type of load model = ", data["load"][load]["model"])

            # println("position 2")
            data_new["load"][load]["pd"]  = adc_sumloads[adc][:,1]
            # println("position 3")
            data_new["load"][load]["qd"] = adc_sumloads[adc][:,2]
            # println("position 4")
            data_new["load"][load]["model"] = "constant_power"
        else
            load_dict = deepcopy(data_new["load"]["1"])
            load_dict["name"] = ""
            load_dict["conn"] = "wye"
            load_dict["model"] = "constant_power"
            load_dict["active_phases"] = [1, 2, 3]
            load_dict["load_bus"] = parse(Int64,adc)
            load_dict["pd"] = adc_sumloads[adc][:,1]
            load_dict["qd"] = adc_sumloads[adc][:,2]
            load_dict["source_id"] = ""
            load_indices = collect(parse(Int64,num) for (num,l) in data_new["load"])
            new_index = maximum(load_indices) + 1
            load_dict["index"] = new_index
            data_new["load"][string(new_index)] = load_dict

            bus_loads[adc] = [string(new_index)]
            # @show length(data_new["load"])
            println("added new load")
        end

    end

    # remove loads
    for (adc,control_area) in ADC_pm
        # control_area_trimmed = control_area
        control_area_trimmed = setdiff(control_area,[adc])
        for bus in control_area_trimmed
            if bus in keys(bus_loads)
                for load in bus_loads[bus]
                    delete!(data_new["load"],load)
                end
            end
        end
    end
    for adc in keys(ADC_pm)
        if adc in keys(bus_loads)
            loads = bus_loads[adc]
            if length(loads) > 1
                println("Indeed too many loads at an ADC")
                for i=2:length(loads)
                    load = loads[i]
                    delete!(data_new["load"],load)
                end
            end
        end
    end

    return data_new
end
# end of data surgery


# parse adc flexibility regions
function build_adc_flex_model(filename_flex, data)

    pm_to_source, source_to_pm = build_bus_renaming_dict(data)

    data_source = CSV.read(filename_flex)
    adc_flex = Dict{String,Array{Float64,2}}()
    for i=1:size(data_source,1)
        adc_name = data_source[i,1]
        pos = findfirst(isequal('C'), adc_name)
        adc_name = adc_name[pos+1:end]
        intervals = split(data_source[i,end],"|")
        pmin = parse(Float64,intervals[1][2:end])
        pmax = parse(Float64,intervals[2])
        qmin = parse(Float64,intervals[3])
        qmax = parse(Float64,intervals[4][1:end-1])

        # if parse(Int64,adc_name) == 52
        #     # custom changes to ADC at node 52
        #
        #
        #     # ADC["52"] = ["52"]
        #     # ADC["53"] = ["53"]
        #     # ADC["54"]= ["54","55","56"]
        #     # ADC["57"] = ["57","58","59"]
        #     # ADC["60"] = ["60","61"]
        # else
            # convert to pm index
        adc_name = source_to_pm[adc_name]
        adc_flex[adc_name]  = [pmin pmax; qmin qmax]
        # end

    end



    return adc_flex
end





# auxiliary functions
function build_ADC_list(filename)
    adc_raw_data = CSV.read(filename)
    adc_raw_data = adc_raw_data[2:2:end,:]


    adc_bus_numbers = unique!(collect(adc_raw_data[i,end] for i=1:size(adc_raw_data,1)))
    adc_bus_numbers = adc_bus_numbers[2:end]

    ADC = Dict{String,Array{String,1}}()

    for i in adc_bus_numbers
        ADC[i] = []
    end

    for i=1:size(adc_raw_data,1)
        if adc_raw_data[i,end]!= "NONE"
            adc_bus_num = adc_raw_data[i,end]
            bus_num = string(adc_raw_data[i,1])
            push!(ADC[adc_bus_num],bus_num)
        end
    end
    # @show ADC


    # custom changes to ADC at node 52
    # delete!(ADC,"52")
    #
    # ADC["52"] = ["52"]
    # ADC["53"] = ["53"]
    # ADC["54"]= ["54","55","56"]
    # ADC["57"] = ["57","58","59"]
    # ADC["60"] = ["60","61"]

    return ADC
end

function convert_ADC_pm(data,ADC)
    pm_to_source, source_to_pm = build_bus_renaming_dict(data)

    ADC_pm = Dict{String,Array{String,1}}()
    for (adc,control_area) in ADC
        if adc in keys(source_to_pm)
            ADC_pm[source_to_pm[adc]] = collect(source_to_pm[b] for b in control_area if b in keys(source_to_pm))
        end
    end

    return ADC_pm
end


function build_bus_renaming_dict(data)
    source_to_pm = Dict{String,String}()
    pm_to_source = Dict{String,String}()
    for (i,bus) in data["bus"]
        if "source_id" in keys(bus)
            continue
        else
            pm_to_source[i] = bus["name"]
            source_to_pm[bus["name"]] = i
        end
    end
    return pm_to_source, source_to_pm
end


function build_bus_loads(data)
    load_buses = unique!(collect(string(load["load_bus"]) for (i,load) in data["load"]))
    bus_loads = Dict{String,Array{String,1}}()
    for i in load_buses
        bus_loads[i] = []
    end

    for (i,load) in data["load"]
        push!(bus_loads[string(load["load_bus"])], i)
    end
    # @show bus_loads
    return bus_loads
end


function find_ADC_sumloads(data,ADC,bus_loads)
    adc_sumloads = Dict{String,Array{Float64,2}}()

    for (adc,control_area) in ADC
        adc_sumloads[adc] = [0 0;0 0; 0 0]
        for bus in control_area
            if bus in keys(bus_loads)
                loads = bus_loads[bus]
                for l in loads
                    adc_sumloads[adc] += [data["load"][l]["pd"] data["load"][l]["qd"]]
                end
            end
        end
    end

    return adc_sumloads
end



    # fix bus renaming issues
function find_branches_to_remove(data,ADC)
    branches_to_remove = []
    for (adc,control_area) in ADC
        control_area_trimmed = setdiff(control_area,[adc])
        # branches = []
        for (b,branch) in data["branch"]
            t_bus = data["bus"][string(branch["t_bus"])]["index"]
            f_bus = data["bus"][string(branch["f_bus"])]["index"]
            if string(branch["t_bus"]) in control_area_trimmed
                push!(branches_to_remove,b)
            elseif string(branch["t_bus"]) in control_area_trimmed
                push!(branches_to_remove,b)
            end
        end
    end
    return unique!(branches_to_remove)
end

function branches_to_buspairs(data, branches)
    # fix bus renaming issues

    buspairs = []
    for b in branches
        t_bus = data["branch"][b]["t_bus"]
        f_bus = data["branch"][b]["f_bus"]

        bp = (data["bus"][string(f_bus)]["index"],data["bus"][string(t_bus)]["index"])

        push!(buspairs,bp)
    end
    return buspairs
end


# data = PowerModelsDistribution.parse_file("IEEETestCases/123Bus_GMLC/IEEE123Master.dss")
