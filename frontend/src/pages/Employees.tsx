
import { useEffect, useMemo, useState } from 'react'
import { apiRequest } from '../lib/api'
import './Employees.css'

type Master = {
  id: number
  name: string
  is_active: boolean
  division_id?: number
  department_id?: number
}

type Employee = {
  id: number
  employee_code: string
  name: string
  contract_type: string
  joining_date: string
  location_id: number
  division_id: number
  department_id: number
  sub_department_id: number | null
  designation_id: number
  reporting_manager_id: number | null
  is_active: boolean
}

type EmployeeForm = {
  name: string
  contract_type: string
  joining_date: string
  location_id: string
  division_id: string
  department_id: string
  sub_department_id: string
  designation_id: string
  reporting_manager_id: string
  third_party: boolean
  third_party_company: string
  pf_deduction_allowed: boolean
  eobi_enabled: boolean
  eobi_number: string
  eobi_registration_date: string
  essi_enabled: boolean
  essi_number: string
  essi_registration_date: string
  zakat_exemption: boolean
  interest_free_pf_account: boolean
}

const emptyForm: EmployeeForm = {
  name: '',
  contract_type: 'Permanent',
  joining_date: '',
  location_id: '',
  division_id: '',
  department_id: '',
  sub_department_id: '',
  designation_id: '',
  reporting_manager_id: '',
  third_party: false,
  third_party_company: '',
  pf_deduction_allowed: false,
  eobi_enabled: false,
  eobi_number: '',
  eobi_registration_date: '',
  essi_enabled: false,
  essi_number: '',
  essi_registration_date: '',
  zakat_exemption: false,
  interest_free_pf_account: false,
}

function Employees() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [locations, setLocations] = useState<Master[]>([])
  const [divisions, setDivisions] = useState<Master[]>([])
  const [departments, setDepartments] = useState<Master[]>([])
  const [subDepartments, setSubDepartments] = useState<Master[]>([])
  const [designations, setDesignations] = useState<Master[]>([])

  const [form, setForm] = useState<EmployeeForm>(emptyForm)
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [search, setSearch] = useState('')

  const pfEligible = !['Contractual', 'Intern'].includes(form.contract_type)

  async function loadEmployees() {
    const data = await apiRequest<Employee[]>('/api/v1/employees/')
    setEmployees(data)
  }

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        setError('')

        const [
          employeeData,
          locationData,
          divisionData,
          departmentData,
          subDepartmentData,
          designationData,
        ] = await Promise.all([
          apiRequest<Employee[]>('/api/v1/employees/'),
          apiRequest<Master[]>('/api/v1/organization/locations/'),
          apiRequest<Master[]>('/api/v1/organization/divisions/'),
          apiRequest<Master[]>('/api/v1/organization/departments/'),
          apiRequest<Master[]>('/api/v1/organization/sub-departments/'),
          apiRequest<Master[]>('/api/v1/organization/designations/'),
        ])

        setEmployees(employeeData)
        setLocations(locationData.filter((item) => item.is_active))
        setDivisions(divisionData.filter((item) => item.is_active))
        setDepartments(departmentData.filter((item) => item.is_active))
        setSubDepartments(subDepartmentData.filter((item) => item.is_active))
        setDesignations(designationData.filter((item) => item.is_active))
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Data load failed')
      } finally {
        setLoading(false)
      }
    }

    void loadData()
  }, [])

  const filteredDepartments = useMemo(
    () =>
      departments.filter(
        (item) => item.division_id === Number(form.division_id),
      ),
    [departments, form.division_id],
  )

  const filteredSubDepartments = useMemo(
    () =>
      subDepartments.filter(
        (item) => item.department_id === Number(form.department_id),
      ),
    [subDepartments, form.department_id],
  )

  const managers = employees.filter((employee) => employee.is_active)

  const filteredEmployees = employees.filter((employee) => {
    const query = search.toLowerCase()
    return (
      employee.name.toLowerCase().includes(query) ||
      employee.employee_code.toLowerCase().includes(query)
    )
  })

  function updateField<K extends keyof EmployeeForm>(
    key: K,
    value: EmployeeForm[K],
  ) {
    setForm((previous) => ({ ...previous, [key]: value }))
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSuccess('')

        if (
      !form.name.trim() ||
      !form.contract_type ||
      !form.joining_date ||
      !form.location_id ||
      !form.division_id ||
      !form.department_id ||
      !form.designation_id
    ) {
      setError('Please complete all required fields.')
      return
    }

    const payload = {
      name: form.name.trim(),
      contract_type: form.contract_type,
      joining_date: form.joining_date,
      location_id: Number(form.location_id),
      division_id: Number(form.division_id),
      department_id: Number(form.department_id),
      sub_department_id: form.sub_department_id
        ? Number(form.sub_department_id)
        : null,
      designation_id: Number(form.designation_id),
      reporting_manager_id: form.reporting_manager_id
        ? Number(form.reporting_manager_id)
        : null,
      third_party: form.third_party,
      third_party_company: form.third_party
        ? form.third_party_company.trim() || null
        : null,
      pf_deduction_allowed: pfEligible && form.pf_deduction_allowed,
      eobi_enabled: form.eobi_enabled,
      eobi_number: form.eobi_enabled ? form.eobi_number || null : null,
      eobi_registration_date: form.eobi_enabled
        ? form.eobi_registration_date || null
        : null,
      essi_enabled: form.essi_enabled,
      essi_number: form.essi_enabled ? form.essi_number || null : null,
      essi_registration_date: form.essi_enabled
        ? form.essi_registration_date || null
        : null,
      zakat_exemption: form.zakat_exemption,
      interest_free_pf_account: pfEligible && form.interest_free_pf_account,
    }

    try {
      setSaving(true)
      await apiRequest<Employee>('/api/v1/employees/', {
        method: 'POST',
        body: JSON.stringify(payload),
      })

      await loadEmployees()
      setForm(emptyForm)
      setShowForm(false)
      setSuccess('Employee created successfully.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Employee creation failed')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="employee-message">Loading employees...</div>

  return (
    <section className="employees-page">
      <div className="employees-header">
        <div>
          <h1>Employees</h1>
          <p>Manage employee profiles and records</p>
        </div>

        <button
          className="employee-primary-btn"
          onClick={() => {
            setError('')
            setSuccess('')
            setShowForm(!showForm)
          }}
        >
          {showForm ? 'Back to Employees' : '+ Add Employee'}
        </button>
      </div>

      {error && <div className="employee-error">{error}</div>}
      {success && <div className="employee-success">{success}</div>}

      {showForm ? (
        <form className="employee-form" onSubmit={handleSubmit}>
          <h2>Employee Profile</h2>

          <div className="employee-form-grid">
            <label>
              Employee Name *
              <input required maxLength={150} value={form.name}
                onChange={(e) => updateField('name', e.target.value)} />
            </label>

            <label>
              Contract Type *
              <select value={form.contract_type}
                onChange={(e) => {
                  const value = e.target.value
                  setForm((old) => ({
                    ...old,
                    contract_type: value,
                    pf_deduction_allowed: ['Contractual', 'Intern'].includes(value)
                      ? false : old.pf_deduction_allowed,
                    interest_free_pf_account: ['Contractual', 'Intern'].includes(value)
                      ? false : old.interest_free_pf_account,
                  }))
                }}>
                {['Permanent', 'Contractual', 'Probation', 'Intern', 'Third Party', 'Temporary'].map((item) =>
                  <option key={item}>{item}</option>
                )}
              </select>
            </label>

            <label>
              Joining Date *
              <input required type="date" value={form.joining_date}
                onChange={(e) => updateField('joining_date', e.target.value)} />
            </label>

            <label>
              Location *
              <select required value={form.location_id}
                onChange={(e) => updateField('location_id', e.target.value)}>
                <option value="">Select Location</option>
                {locations.map((item) =>
                  <option key={item.id} value={item.id}>{item.name}</option>
                )}
              </select>
            </label>

            <label>
              Division *
              <select required value={form.division_id}
                onChange={(e) => setForm((old) => ({
                  ...old,
                  division_id: e.target.value,
                  department_id: '',
                  sub_department_id: '',
                }))}>
                <option value="">Select Division</option>
                {divisions.map((item) =>
                  <option key={item.id} value={item.id}>{item.name}</option>
                )}
              </select>
            </label>

            <label>
              Department *
              <select required value={form.department_id}
                disabled={!form.division_id}
                onChange={(e) => setForm((old) => ({
                  ...old,
                  department_id: e.target.value,
                  sub_department_id: '',
                }))}>
                <option value="">Select Department</option>
                {filteredDepartments.map((item) =>
                  <option key={item.id} value={item.id}>{item.name}</option>
                )}
              </select>
            </label>

            <label>
              Sub-Department
              <select value={form.sub_department_id}
                disabled={!form.department_id}
                onChange={(e) => updateField('sub_department_id', e.target.value)}>
                <option value="">None</option>
                {filteredSubDepartments.map((item) =>
                  <option key={item.id} value={item.id}>{item.name}</option>
                )}
              </select>
            </label>

            <label>
              Designation *
              <select required value={form.designation_id}
                onChange={(e) => updateField('designation_id', e.target.value)}>
                <option value="">Select Designation</option>
                {designations.map((item) =>
                  <option key={item.id} value={item.id}>{item.name}</option>
                )}
              </select>
            </label>

            <label>
              Reporting Manager
              <select
                value={form.reporting_manager_id}
                onChange={(e) =>
                  updateField('reporting_manager_id', e.target.value)
                }
              >
                <option value="">No Reporting Manager (Root Employee)</option>
                {managers.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.employee_code} - {item.name}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <h3>Employment Details</h3>
          <label className="employee-check">
            <input type="checkbox" checked={form.third_party}
              onChange={(e) => updateField('third_party', e.target.checked)} />
            Third Party Employee
          </label>

          {form.third_party && (
            <label>
              Third Party Company
              <input value={form.third_party_company}
                onChange={(e) => updateField('third_party_company', e.target.value)} />
            </label>
          )}

          <h3>Provident Fund</h3>
          {!pfEligible && <p>PF is not applicable to Contractual and Intern employees.</p>}
          <label className="employee-check">
            <input type="checkbox" disabled={!pfEligible}
              checked={form.pf_deduction_allowed}
              onChange={(e) => updateField('pf_deduction_allowed', e.target.checked)} />
            PF Deduction Allowed
          </label>
          <label className="employee-check">
            <input type="checkbox" disabled={!pfEligible}
              checked={form.zakat_exemption}
              onChange={(e) => updateField('zakat_exemption', e.target.checked)} />
            Zakat Exemption
          </label>
          <label className="employee-check">
            <input type="checkbox" disabled={!pfEligible}
              checked={form.interest_free_pf_account}
              onChange={(e) => updateField('interest_free_pf_account', e.target.checked)} />
            Interest-Free PF Account
          </label>

          <h3>EOBI</h3>
          <label className="employee-check">
            <input type="checkbox" checked={form.eobi_enabled}
              onChange={(e) => updateField('eobi_enabled', e.target.checked)} />
            EOBI Enabled
          </label>
          {form.eobi_enabled && (
            <div className="employee-form-grid">
              <label>EOBI Number
                <input value={form.eobi_number}
                  onChange={(e) => updateField('eobi_number', e.target.value)} />
              </label>
              <label>EOBI Registration Date
                <input type="date" value={form.eobi_registration_date}
                  onChange={(e) => updateField('eobi_registration_date', e.target.value)} />
              </label>
            </div>
          )}

          <h3>ESSI</h3>
          <label className="employee-check">
            <input type="checkbox" checked={form.essi_enabled}
              onChange={(e) => updateField('essi_enabled', e.target.checked)} />
            ESSI Enabled
          </label>
          {form.essi_enabled && (
            <div className="employee-form-grid">
              <label>ESSI Number
                <input value={form.essi_number}
                  onChange={(e) => updateField('essi_number', e.target.value)} />
              </label>
              <label>ESSI Registration Date
                <input type="date" value={form.essi_registration_date}
                  onChange={(e) => updateField('essi_registration_date', e.target.value)} />
              </label>
            </div>
          )}

          <div className="employee-form-actions">
            <button type="button" className="employee-secondary-btn"
              onClick={() => setShowForm(false)}>Cancel</button>
            <button type="submit" className="employee-primary-btn" disabled={saving}>
              {saving ? 'Saving...' : 'Save Employee'}
            </button>
          </div>
        </form>
      ) : (
        <>
          <input className="employee-search" placeholder="Search by name or employee code..."
            value={search} onChange={(e) => setSearch(e.target.value)} />

          <div className="employee-table-wrap">
            <table className="employee-table">
              <thead>
                <tr>
                  <th>Employee Code</th>
                  <th>Name</th>
                  <th>Contract Type</th>
                  <th>Joining Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredEmployees.map((employee) => (
                  <tr key={employee.id}>
                    <td>{employee.employee_code}</td>
                    <td>{employee.name}</td>
                    <td>{employee.contract_type}</td>
                    <td>{employee.joining_date}</td>
                    <td>{employee.is_active ? 'Active' : 'Inactive'}</td>
                  </tr>
                ))}
                {filteredEmployees.length === 0 && (
                  <tr><td colSpan={5}>No employees found.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  )
}

export default Employees
