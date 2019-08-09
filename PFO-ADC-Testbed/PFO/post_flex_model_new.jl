using PowerModelsDistribution
using PowerModels
using Ipopt
using JuMP
using DataFrames
using CSV
# using Memento

include("support_functions.jl")


_PMs = PowerModels

function constraint_tp_load_current_delta_mod(pm::_PMs.GenericPowerModel{T}, nw::Int, load_id::Int, load_bus_id::Int, cp::_PMs.MultiConductorVector, cq::_PMs.MultiConductorVector) where T <: _PMs.AbstractACPForm
    cp_ab, cp_bc, cp_ca = cp
    cq_ab, cq_bc, cq_ca = cq
    vm_a, vm_b, vm_c = [_PMs.var(pm, nw, c, :vm, load_bus_id) for c in 1:3]
    va_a, va_b, va_c = [_PMs.var(pm, nw, c, :va, load_bus_id) for c in 1:3]
    # v_xy = v_x - v_y
    vre_xy(vm_x, va_x, vm_y, va_y) = JuMP.@NLexpression(pm.model, vm_x*cos(va_x)-vm_y*cos(va_y))
    vim_xy(vm_x, va_x, vm_y, va_y) = JuMP.@NLexpression(pm.model, vm_x*sin(va_x)-vm_y*sin(va_y))
    vre_ab = vre_xy(vm_a, va_a, vm_b, va_b)
    vim_ab = vim_xy(vm_a, va_a, vm_b, va_b)
    vre_bc = vre_xy(vm_b, va_b, vm_c, va_c)
    vim_bc = vim_xy(vm_b, va_b, vm_c, va_c)
    vre_ca = vre_xy(vm_c, va_c, vm_a, va_a)
    vim_ca = vim_xy(vm_c, va_c, vm_a, va_a)
    # i_xy = conj(s_xy/v_xy)
    ire_xy(cp_xy, cq_xy, vre_xy, vim_xy) = JuMP.@NLexpression(pm.model, 1/sqrt(vre_xy^2+vim_xy^2)*(cp_xy*vre_xy+cq_xy*vim_xy))
    iim_xy(cp_xy, cq_xy, vre_xy, vim_xy) = JuMP.@NLexpression(pm.model, 1/sqrt(vre_xy^2+vim_xy^2)*(cp_xy*vim_xy-cq_xy*vre_xy))
    ire_ab = ire_xy(cp_ab, cq_ab, vre_ab, vim_ab)
    iim_ab = iim_xy(cp_ab, cq_ab, vre_ab, vim_ab)
    ire_bc = ire_xy(cp_bc, cq_bc, vre_bc, vim_bc)
    iim_bc = iim_xy(cp_bc, cq_bc, vre_bc, vim_bc)
    ire_ca = ire_xy(cp_ca, cq_ca, vre_ca, vim_ca)
    iim_ca = iim_xy(cp_ca, cq_ca, vre_ca, vim_ca)
    # s_x = v_x*conj(i_xy-i_zx)
    # p_x = vm_x*cos(va_x)*(ire_xy-ire_zx) + vm_x*sin(va_x)*(iim_xy-iim_zx)
    # q_x = vm_x*sin(va_x)*(ire_xy-ire_zx) - vm_x*cos(va_x)*(iim_xy-iim_zx)
    p_x(vm_x, va_x, ire_xy, iim_xy, ire_zx, iim_zx) = JuMP.@NLexpression(pm.model, vm_x*cos(va_x)*(ire_xy-ire_zx) + vm_x*sin(va_x)*(iim_xy-iim_zx))
    q_x(vm_x, va_x, ire_xy, iim_xy, ire_zx, iim_zx) = JuMP.@NLexpression(pm.model, vm_x*sin(va_x)*(ire_xy-ire_zx) - vm_x*cos(va_x)*(iim_xy-iim_zx))
    # s_x = s_x,ref
    _PMs.var(pm, nw, 1, :pd)[load_id] = p_x(vm_a, va_a, ire_ab, iim_ab, ire_ca, iim_ca)
    _PMs.var(pm, nw, 2, :pd)[load_id] = p_x(vm_b, va_b, ire_bc, iim_bc, ire_ab, iim_ab)
    _PMs.var(pm, nw, 3, :pd)[load_id] = p_x(vm_c, va_c, ire_ca, iim_ca, ire_bc, iim_bc)
    _PMs.var(pm, nw, 1, :qd)[load_id] = q_x(vm_a, va_a, ire_ab, iim_ab, ire_ca, iim_ca)
    _PMs.var(pm, nw, 2, :qd)[load_id] = q_x(vm_b, va_b, ire_bc, iim_bc, ire_ab, iim_ab)
    _PMs.var(pm, nw, 3, :qd)[load_id] = q_x(vm_c, va_c, ire_ca, iim_ca, ire_bc, iim_bc)
end




function constraint_tp_load_impedance_delta_mod(pm::_PMs.GenericPowerModel{T}, nw::Int, load_id::Int, load_bus_id::Int, cp::_PMs.MultiConductorVector, cq::_PMs.MultiConductorVector) where T <: _PMs.AbstractACPForm
    cp_ab, cp_bc, cp_ca = cp
    cq_ab, cq_bc, cq_ca = cq
    vm_a, vm_b, vm_c = [_PMs.var(pm, nw, c, :vm, load_bus_id) for c in 1:3]
    va_a, va_b, va_c = [_PMs.var(pm, nw, c, :va, load_bus_id) for c in 1:3]
    # v_xy = v_x - v_y
    vre_xy(vm_x, va_x, vm_y, va_y) = JuMP.@NLexpression(pm.model, vm_x*cos(va_x)-vm_y*cos(va_y))
    vim_xy(vm_x, va_x, vm_y, va_y) = JuMP.@NLexpression(pm.model, vm_x*sin(va_x)-vm_y*sin(va_y))
    vre_ab = vre_xy(vm_a, va_a, vm_b, va_b)
    vim_ab = vim_xy(vm_a, va_a, vm_b, va_b)
    vre_bc = vre_xy(vm_b, va_b, vm_c, va_c)
    vim_bc = vim_xy(vm_b, va_b, vm_c, va_c)
    vre_ca = vre_xy(vm_c, va_c, vm_a, va_a)
    vim_ca = vim_xy(vm_c, va_c, vm_a, va_a)
    # i_xy = conj(s_xy/v_xy)
    ire_xy(cp_xy, cq_xy, vre_xy, vim_xy) = JuMP.@NLexpression(pm.model, cp_xy*vre_xy+cq_xy*vim_xy)
    iim_xy(cp_xy, cq_xy, vre_xy, vim_xy) = JuMP.@NLexpression(pm.model, cp_xy*vim_xy-cq_xy*vre_xy)
    ire_ab = ire_xy(cp_ab, cq_ab, vre_ab, vim_ab)
    iim_ab = iim_xy(cp_ab, cq_ab, vre_ab, vim_ab)
    ire_bc = ire_xy(cp_bc, cq_bc, vre_bc, vim_bc)
    iim_bc = iim_xy(cp_bc, cq_bc, vre_bc, vim_bc)
    ire_ca = ire_xy(cp_ca, cq_ca, vre_ca, vim_ca)
    iim_ca = iim_xy(cp_ca, cq_ca, vre_ca, vim_ca)
    # s_x = v_x*conj(i_xy-i_zx)
    # p_x = vm_x*cos(va_x)*(ire_xy-ire_zx) + vm_x*sin(va_x)*(iim_xy-iim_zx)
    # q_x = vm_x*sin(va_x)*(ire_xy-ire_zx) - vm_x*cos(va_x)*(iim_xy-iim_zx)
    p_x(vm_x, va_x, ire_xy, iim_xy, ire_zx, iim_zx) = JuMP.@NLexpression(pm.model, vm_x*cos(va_x)*(ire_xy-ire_zx) + vm_x*sin(va_x)*(iim_xy-iim_zx))
    q_x(vm_x, va_x, ire_xy, iim_xy, ire_zx, iim_zx) = JuMP.@NLexpression(pm.model, vm_x*sin(va_x)*(ire_xy-ire_zx) - vm_x*cos(va_x)*(iim_xy-iim_zx))
    # s_x = s_x,ref
    _PMs.var(pm, nw, 1, :pd)[load_id] = p_x(vm_a, va_a, ire_ab, iim_ab, ire_ca, iim_ca)
    _PMs.var(pm, nw, 2, :pd)[load_id] = p_x(vm_b, va_b, ire_bc, iim_bc, ire_ab, iim_ab)
    _PMs.var(pm, nw, 3, :pd)[load_id] = p_x(vm_c, va_c, ire_ca, iim_ca, ire_bc, iim_bc)
    _PMs.var(pm, nw, 1, :qd)[load_id] = q_x(vm_a, va_a, ire_ab, iim_ab, ire_ca, iim_ca)
    _PMs.var(pm, nw, 2, :qd)[load_id] = q_x(vm_b, va_b, ire_bc, iim_bc, ire_ab, iim_ab)
    _PMs.var(pm, nw, 3, :qd)[load_id] = q_x(vm_c, va_c, ire_ca, iim_ca, ire_bc, iim_bc)
end

function constraint_load_current_wye_mod(pm::_PMs.GenericPowerModel{T}, nw::Int, cnd::Int, load_id::Int, load_bus_id::Int, scale_p::Real, scale_q::Real) where T <: _PMs.AbstractACPForm
    vm = _PMs.var(pm, nw, cnd, :vm, load_bus_id)
    # this has to be a NLexpression and not an expression;
    # might be mixed in KCL with NLexpression, so has to also be NLexpression
    # original expression
    # _PMs.var(pm, nw, cnd, :pd)[load_id] = JuMP.@NLexpression(pm.model, scale_p*vm)
    # _PMs.var(pm, nw, cnd, :qd)[load_id] = JuMP.@NLexpression(pm.model, scale_q*vm)
    # end of original expression
    # _PMs.var(pm, nw, cnd, :pd)[load_id] = JuMP.@NLexpression(pm.model, scale_p*vm*1.02)
    # _PMs.var(pm, nw, cnd, :qd)[load_id] = JuMP.@NLexpression(pm.model, scale_q*vm*1.02)
    _PMs.var(pm, nw, cnd, :pd)[load_id] = JuMP.@variable(pm.model)
    _PMs.var(pm, nw, cnd, :qd)[load_id] = JuMP.@variable(pm.model)
    JuMP.@constraint(pm.model, _PMs.var(pm, nw, cnd, :pd)[load_id] == scale_p*vm)
    JuMP.@constraint(pm.model, _PMs.var(pm, nw, cnd, :qd)[load_id] == scale_q*vm)

    # JuMP.@constraint(pm.model, _PMs.var(pm, nw, cnd, :pd)[load_id] <=  scale_p*vm*(1.02))
    # JuMP.@constraint(pm.model, _PMs.var(pm, nw, cnd, :qd)[load_id] <=  scale_q*vm*(1.02))
    # JuMP.@constraint(pm.model, scale_p*vm*(0.98) <= _PMs.var(pm, nw, cnd, :pd)[load_id])
    # JuMP.@constraint(pm.model, scale_q*vm*(0.98) <= _PMs.var(pm, nw, cnd, :qd)[load_id])
    # JuMP.@NLexpression(pm.model, scale_q*vm*(0.98)) <=
    # JuMP.@NLexpression(pm.model, scale_p*vm*(0.98)) <=
end

function constraint_load_impedance_wye_mod(pm::_PMs.GenericPowerModel{T}, nw::Int, cnd::Int, load_id::Int, load_bus_id::Int, cp::Real, cq::Real) where T <: _PMs.AbstractACPForm
    vm = _PMs.var(pm, nw, cnd, :vm, load_bus_id)
    _PMs.var(pm, nw, cnd, :pd)[load_id] = JuMP.@NLexpression(pm.model, cp*vm^2)
    _PMs.var(pm, nw, cnd, :qd)[load_id] = JuMP.@NLexpression(pm.model, cq*vm^2)
end

# this is the only function really required
function constraint_load_power_wye_mod(pm::_PMs.GenericPowerModel{T}, nw::Int, cnd::Int, load_id::Int, pd::Real, qd::Real, adc_flex) where T <: _PMs.AbstractACPForm
    # _PMs.var(pm, nw, cnd, :pd)[load_id] = pd
    # _PMs.var(pm, nw, cnd, :qd)[load_id] = qd


    # println("we are in constatn load power y model")
    # @show load_id
    _PMs.var(pm, nw, cnd, :pd)[load_id] = JuMP.@variable(pm.model, start = pd)
    _PMs.var(pm, nw, cnd, :qd)[load_id] = JuMP.@variable(pm.model, start = qd)

    load_bus = pm.data["load"][string(load_id)]["load_bus"]
    if string(load_bus) in keys(adc_flex)
        flex_region = adc_flex[string(load_bus)]*1e-5
        # @show flex_region

#        println("Splitting flex region into phases ...")

        pd_original = pm.data["load"][string(load_id)]["pd"]
        qd_original = pm.data["load"][string(load_id)]["qd"]

        pmin = flex_region[1,2]
        pmax = flex_region[1,1]
        qmin = flex_region[2,2]
        qmax = flex_region[2,1]
        #
        pmin = pmin*pd_original[cnd]/sum(pd_original)
        pmax = pmax*pd_original[cnd]/sum(pd_original)
        qmin = qmin*qd_original[cnd]/sum(qd_original)
        qmax = qmax*qd_original[cnd]/sum(qd_original)
        #
        # pmin = pd*0.8
        # pmax = pd*1.2
        # qmin = qd*0.8
        # qmax = qd*1.2
        #
        # pmin = pd
        # pmax = pd
        # qmin = qd
        # qmax = qd

        # @show pd, qd
        # if pmin > pd || pmax < pd || qmin > qd || qmax < qd
        #     println("Infeasible constraints!!!")
        # end

        # # println("Adding flex constraints for ADC ", string(load_bus))
        JuMP.@constraint(pm.model, _PMs.var(pm, nw, cnd, :pd)[load_id] >=  pmin)
        JuMP.@constraint(pm.model, _PMs.var(pm, nw, cnd, :pd)[load_id] <=  pmax)
        JuMP.@constraint(pm.model, _PMs.var(pm, nw, cnd, :qd)[load_id] >=  qmin)
        JuMP.@constraint(pm.model, _PMs.var(pm, nw, cnd, :qd)[load_id] <=  qmax)
    else
        JuMP.@constraint(pm.model, _PMs.var(pm, nw, cnd, :pd)[load_id] ==  pd)
        JuMP.@constraint(pm.model, _PMs.var(pm, nw, cnd, :qd)[load_id] ==  qd)
    end




    # JuMP.@constraint(pm.model, _PMs.var(pm, nw, cnd, :pd)[load_id] <=  pd*1.02)
    # JuMP.@constraint(pm.model, _PMs.var(pm, nw, cnd, :qd)[load_id] <=  qd*1.02)
    # JuMP.@constraint(pm.model, pd*0.98 <= _PMs.var(pm, nw, cnd, :pd)[load_id])
    # JuMP.@constraint(pm.model, qd*0.98 <= _PMs.var(pm, nw, cnd, :qd)[load_id])
end


function constraint_tp_load_power_delta_mod(pm::_PMs.GenericPowerModel{T}, nw::Int, load_id::Int, load_bus_id::Int, pd::_PMs.MultiConductorVector, qd::_PMs.MultiConductorVector) where T <: _PMs.AbstractACPForm
    p_ab, p_bc, p_ca = pd
    q_ab, q_bc, q_ca = qd
    vm_a, vm_b, vm_c = [_PMs.var(pm, nw, c, :vm, load_bus_id) for c in 1:3]
    va_a, va_b, va_c = [_PMs.var(pm, nw, c, :va, load_bus_id) for c in 1:3]
    # v_xy = v_x - v_y
    vre_xy(vm_x, va_x, vm_y, va_y) = JuMP.@NLexpression(pm.model, vm_x*cos(va_x)-vm_y*cos(va_y))
    vim_xy(vm_x, va_x, vm_y, va_y) = JuMP.@NLexpression(pm.model, vm_x*sin(va_x)-vm_y*sin(va_y))
    vre_ab = vre_xy(vm_a, va_a, vm_b, va_b)
    vim_ab = vim_xy(vm_a, va_a, vm_b, va_b)
    vre_bc = vre_xy(vm_b, va_b, vm_c, va_c)
    vim_bc = vim_xy(vm_b, va_b, vm_c, va_c)
    vre_ca = vre_xy(vm_c, va_c, vm_a, va_a)
    vim_ca = vim_xy(vm_c, va_c, vm_a, va_a)
    # i_xy = conj(s_xy/v_xy)
    ire_xy(p_xy, q_xy, vre_xy, vim_xy) = JuMP.@NLexpression(pm.model, (p_xy*vre_xy+q_xy*vim_xy)/(vre_xy^2+vim_xy^2))
    iim_xy(p_xy, q_xy, vre_xy, vim_xy) = JuMP.@NLexpression(pm.model, (p_xy*vim_xy-q_xy*vre_xy)/(vre_xy^2+vim_xy^2))
    ire_ab = ire_xy(p_ab, q_ab, vre_ab, vim_ab)
    iim_ab = iim_xy(p_ab, q_ab, vre_ab, vim_ab)
    ire_bc = ire_xy(p_bc, q_bc, vre_bc, vim_bc)
    iim_bc = iim_xy(p_bc, q_bc, vre_bc, vim_bc)
    ire_ca = ire_xy(p_ca, q_ca, vre_ca, vim_ca)
    iim_ca = iim_xy(p_ca, q_ca, vre_ca, vim_ca)
    # s_x = v_x*conj(i_xy-i_zx)
    # p_x = vm_x*cos(va_x)*(ire_xy-ire_zx) + vm_x*sin(va_x)*(iim_xy-iim_zx)
    # q_x = vm_x*sin(va_x)*(ire_xy-ire_zx) - vm_x*cos(va_x)*(iim_xy-iim_zx)
    p_x(vm_x, va_x, ire_xy, iim_xy, ire_zx, iim_zx) = JuMP.@NLexpression(pm.model, vm_x*cos(va_x)*(ire_xy-ire_zx) + vm_x*sin(va_x)*(iim_xy-iim_zx))
    q_x(vm_x, va_x, ire_xy, iim_xy, ire_zx, iim_zx) = JuMP.@NLexpression(pm.model, vm_x*sin(va_x)*(ire_xy-ire_zx) - vm_x*cos(va_x)*(iim_xy-iim_zx))
    # s_x = s_x,ref
    _PMs.var(pm, nw, 1, :pd)[load_id] = p_x(vm_a, va_a, ire_ab, iim_ab, ire_ca, iim_ca)
    _PMs.var(pm, nw, 2, :pd)[load_id] = p_x(vm_b, va_b, ire_bc, iim_bc, ire_ab, iim_ab)
    _PMs.var(pm, nw, 3, :pd)[load_id] = p_x(vm_c, va_c, ire_ca, iim_ca, ire_bc, iim_bc)
    _PMs.var(pm, nw, 1, :qd)[load_id] = q_x(vm_a, va_a, ire_ab, iim_ab, ire_ca, iim_ca)
    _PMs.var(pm, nw, 2, :qd)[load_id] = q_x(vm_b, va_b, ire_bc, iim_bc, ire_ab, iim_ab)
    _PMs.var(pm, nw, 3, :qd)[load_id] = q_x(vm_c, va_c, ire_ca, iim_ca, ire_bc, iim_bc)
end




function constraint_tp_load_mod(pm::_PMs.GenericPowerModel, id::Int, adc_flex; nw=pm.cnw)
    load = _PMs.ref(pm, nw, :load, id)
    model = load["model"]
    conn = _PMs.ref(pm, nw, :load, id, "conn")
    @assert(conn in ["delta", "wye"])

    if model=="constant_power"
        pd = load["pd"]
        qd = load["qd"]

        if conn=="wye"
            for c in _PMs.conductor_ids(pm)
                constraint_load_power_wye_mod(pm, nw, c, id, pd[c], qd[c], adc_flex)
            end
        elseif conn=="delta"
            @assert(_PMs.ref(pm, 0, :conductors)==3)
            constraint_tp_load_power_delta_mod(pm, nw, id, load["load_bus"], pd, qd)
        end

    elseif model=="constant_current"
        vnom_kv = load["vnom_kv"]
        vbase_kv_LL = _PMs.ref(pm, nw, :bus, load["load_bus"])["base_kv"]
        vbase_kv_LN = vbase_kv_LL/sqrt(3)

        pd = load["pd"]
        qd = load["qd"]
        cp = pd/(vnom_kv/vbase_kv_LN)
        cq = qd/(vnom_kv/vbase_kv_LN)

        if conn=="wye"
            for c in _PMs.conductor_ids(pm)
                constraint_load_current_wye_mod(pm, nw, c, id, load["load_bus"], cp[c], cq[c])
            end
        elseif conn=="delta"
            @assert(_PMs.ref(pm, 0, :conductors)==3)
            constraint_tp_load_current_delta_mod(pm, nw, id, load["load_bus"], cp, cq)
        end

    elseif model=="constant_impedance"
        vnom_kv = load["vnom_kv"]
        vbase_kv_LL = _PMs.ref(pm, nw, :bus, load["load_bus"])["base_kv"]
        vbase_kv_LN = vbase_kv_LL/sqrt(3)

        pd = load["pd"]
        qd = load["qd"]
        cp = pd/(vnom_kv/vbase_kv_LN)^2
        cq = qd/(vnom_kv/vbase_kv_LN)^2

        if conn=="wye"
            for c in _PMs.conductor_ids(pm)
                constraint_load_impedance_wye_mod(pm, nw, c, id, load["load_bus"], cp[c], cq[c])
            end
        elseif conn=="delta"
            @assert(_PMs.ref(pm, 0, :conductors)==3)
            constraint_tp_load_impedance_delta_mod(pm, nw, id, load["load_bus"], cp, cq)
        end

    else
        # Memento.@error(LOGGER, "Unknown model $model for load $id.")
    end
end


function post_tp_opf_lm_mod(pm::_PMs.GenericPowerModel)
    variable_tp_voltage(pm)
    variable_tp_branch_flow(pm)

    for c in _PMs.conductor_ids(pm)
        _PMs.variable_generation(pm, cnd=c)
        variable_load(pm, cnd=c)
        _PMs.variable_dcline_flow(pm, cnd=c)
    end
    variable_tp_trans_flow(pm)

    constraint_tp_model_voltage(pm)

    for i in _PMs.ids(pm, :ref_buses)
        constraint_tp_theta_ref(pm, i)
    end

    # loads should be constrained before KCL, or Pd/Qd undefined
    adc_flex = build_adc_flex_model(filename_flex, pm.data)
    for id in _PMs.ids(pm, :load)
        constraint_tp_load_mod(pm, id, adc_flex)
    end

    for i in _PMs.ids(pm, :bus), c in _PMs.conductor_ids(pm)
        constraint_tp_power_balance_shunt_trans_load(pm, i, cnd=c)
    end

    for i in _PMs.ids(pm, :branch)
        for c in _PMs.conductor_ids(pm)
            constraint_tp_ohms_yt_from(pm, i, cnd=c)
            constraint_tp_ohms_yt_to(pm, i, cnd=c)

            _PMs.constraint_voltage_angle_difference(pm, i, cnd=c)

            _PMs.constraint_thermal_limit_from(pm, i, cnd=c)
            _PMs.constraint_thermal_limit_to(pm, i, cnd=c)
        end
    end

    for i in _PMs.ids(pm, :dcline), c in _PMs.conductor_ids(pm)
        _PMs.constraint_dcline(pm, i, cnd=c)
    end

    for i in _PMs.ids(pm, :trans)
        constraint_tp_trans(pm, i)
    end

    # _PMs.objective_min_fuel_cost(pm)
    JuMP.@NLobjective(pm.model,Min, 100*(_PMs.var(pm, 0, 1, :pg)[1] + _PMs.var(pm, 0, 2, :pg)[1] + _PMs.var(pm, 0, 3, :pg)[1])
        + 1e5*sum((_PMs.var(pm, 0, i, :pd)[load_id] - pm.data["load"][string(load_id)]["pd"][i])^2  for load_id in _PMs.ids(pm, :load), i=1:3)
        + 1e5*sum((_PMs.var(pm, 0, i, :qd)[load_id] - pm.data["load"][string(load_id)]["qd"][i])^2  for load_id in _PMs.ids(pm, :load), i=1:3)
        )
end



# result_new = _PMs.run_model(data_new, ACPPowerModel, with_optimizer(Ipopt.Optimizer), post_tp_opf_lm_mod; multiconductor=true, ref_extensions=[ref_add_arcs_trans!])

# Changing load bounds
