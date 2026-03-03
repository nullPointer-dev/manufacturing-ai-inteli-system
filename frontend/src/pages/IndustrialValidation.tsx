import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { DollarSign, TrendingUp, Leaf, Factory, Calculator } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Table, TableBody, TableCell, TableRow } from '@/components/ui/table'
import { industrialValidationApi } from '@/lib/api'
import { formatNumber } from '@/lib/utils'

interface ValidationResult {
  inputs: {
    electricity_cost: number
    batches_per_day: number
    deployment_cost: number
    annual_maintenance_cost: number
    operating_days_per_year: number
    annual_batches: number
  }
  baseline: {
    quality: number
    yield: number
    performance: number
    energy_per_batch: number
    co2_per_batch: number
  }
  optimized: {
    quality: number
    yield: number
    performance: number
    energy_per_batch: number
    co2_per_batch: number
  }
  improvements: {
    quality_improvement_pct: number
    yield_improvement_pct: number
    performance_improvement_pct: number
    energy_saved_per_batch: number
    co2_saved_per_batch: number
  }
  annual_savings: {
    energy_saved_kwh: number
    co2_saved_kg: number
    energy_cost_savings: number
    raw_material_savings: number
    quality_savings: number
    performance_savings: number
    total_savings: number
    net_benefit: number
  }
  financial: {
    roi_3_year_pct: number
    payback_period_years: number
    payback_period_months: number
  }
  environmental: {
    energy_efficiency_improvement_pct: number
    co2_reduction_pct: number
    trees_equivalent: number
  }
  status: string
}

export function IndustrialValidation() {
  // Input parameters
  const [electricityCost, setElectricityCost] = useState(5) // ₹ per kWh
  const [batchesPerDay, setBatchesPerDay] = useState(10)
  const [deploymentCost, setDeploymentCost] = useState(7500000) // ₹ (75L)
  const [annualMaintenanceCost, setAnnualMaintenanceCost] = useState(2000000) // ₹ (20L)
  const [operatingDaysPerYear, setOperatingDaysPerYear] = useState(250)

  const [result, setResult] = useState<ValidationResult | null>(null)

  const calculateMutation = useMutation({
    mutationFn: async () => {
      return industrialValidationApi.calculate({
        electricity_cost: electricityCost,
        batches_per_day: batchesPerDay,
        deployment_cost: deploymentCost,
        annual_maintenance_cost: annualMaintenanceCost,
        operating_days_per_year: operatingDaysPerYear,
      })
    },
    onSuccess: (data) => {
      console.log('Industrial validation result:', data)
      setResult(data)
    },
    onError: (error) => {
      console.error('Calculation error:', error)
    },
  })

  const handleCalculate = () => {
    calculateMutation.mutate()
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-3"
      >
        <Factory className="w-8 h-8 text-blue-500" />
        <div>
          <h1 className="text-3xl font-bold">Industrial Validation</h1>
          <p className="text-muted-foreground">
            Calculate ROI, payback period, and environmental impact with real-time correction engine
          </p>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Parameters */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="border-2 border-blue-500/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="w-5 h-5" />
                Input Parameters
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Electricity Cost */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <Label className="text-sm font-medium">Electricity Cost (₹/kWh)</Label>
                  <span className="text-sm font-bold text-blue-500">
                    ₹{electricityCost.toFixed(3)}
                  </span>
                </div>
                <Slider
                  value={[electricityCost]}
                  onValueChange={(v) => setElectricityCost(v[0])}
                  min={3}
                  max={10}
                  step={0.1}
                  className="py-2"
                />
                <p className="text-xs text-muted-foreground">
                  Typical range: ₹3 - ₹10 per kWh
                </p>
              </div>

              {/* Batches Per Day */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <Label className="text-sm font-medium">Batches Per Day</Label>
                  <span className="text-sm font-bold text-blue-500">
                    {batchesPerDay.toFixed(0)}
                  </span>
                </div>
                <Slider
                  value={[batchesPerDay]}
                  onValueChange={(v) => setBatchesPerDay(v[0])}
                  min={1}
                  max={50}
                  step={1}
                  className="py-2"
                />
                <p className="text-xs text-muted-foreground">
                  Production capacity: 1-50 batches/day
                </p>
              </div>

              {/* Deployment Cost */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <Label className="text-sm font-medium">Deployment Cost (₹)</Label>
                  <span className="text-sm font-bold text-blue-500">
                    ₹{deploymentCost.toLocaleString()}
                  </span>
                </div>
                <Slider
                  value={[deploymentCost]}
                  onValueChange={(v) => setDeploymentCost(v[0])}
                  min={1000000}
                  max={15000000}
                  step={100000}
                  className="py-2"
                />
                <p className="text-xs text-muted-foreground">
                  One-time system deployment: ₹10L - ₹1.5Cr
                </p>
              </div>

              {/* Annual Maintenance Cost */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <Label className="text-sm font-medium">Annual Maintenance Cost (₹)</Label>
                  <span className="text-sm font-bold text-blue-500">
                    ₹{annualMaintenanceCost.toLocaleString()}
                  </span>
                </div>
                <Slider
                  value={[annualMaintenanceCost]}
                  onValueChange={(v) => setAnnualMaintenanceCost(v[0])}
                  min={100000}
                  max={4000000}
                  step={50000}
                  className="py-2"
                />
                <p className="text-xs text-muted-foreground">
                  Annual maintenance: ₹1L - ₹40L per year
                </p>
              </div>

              {/* Operating Days Per Year */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <Label className="text-sm font-medium">Operating Days Per Year</Label>
                  <span className="text-sm font-bold text-blue-500">
                    {operatingDaysPerYear}
                  </span>
                </div>
                <Slider
                  value={[operatingDaysPerYear]}
                  onValueChange={(v) => setOperatingDaysPerYear(v[0])}
                  min={200}
                  max={365}
                  step={5}
                  className="py-2"
                />
                <p className="text-xs text-muted-foreground">
                  Typical: 200-365 days/year
                </p>
              </div>

              {calculateMutation.isError && (
                <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-400">
                  Calculation failed. Please check your inputs and try again.
                </div>
              )}
              <Button
                onClick={handleCalculate}
                disabled={calculateMutation.isPending}
                className="w-full bg-gradient-to-r from-blue-500 to-teal-500 hover:from-blue-600 hover:to-teal-600"
                size="lg"
              >
                {calculateMutation.isPending ? (
                  <>
                    <div className="animate-spin mr-2 h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                    Calculating...
                  </>
                ) : (
                  <>
                    <Calculator className="w-4 h-4 mr-2" />
                    Calculate Validation
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </motion.div>

        {/* Results Overview */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-4"
        >
          {result ? (
            <>
              {/* Financial Metrics */}
              <Card className="border-2 border-green-500/20 bg-gradient-to-br from-green-500/5 to-transparent">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-green-600">
                    <DollarSign className="w-5 h-5" />
                    Financial Impact
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white/50 dark:bg-black/20 rounded-lg p-4 border border-green-500/20">
                      <p className="text-xs text-muted-foreground mb-1">3-Year ROI</p>
                      <p className="text-2xl font-bold text-green-600">
                        {formatNumber(result.financial.roi_3_year_pct)}%
                      </p>
                    </div>
                    <div className="bg-white/50 dark:bg-black/20 rounded-lg p-4 border border-green-500/20">
                      <p className="text-xs text-muted-foreground mb-1">Payback Period</p>
                      <p className="text-2xl font-bold text-green-600">
                        {formatNumber(result.financial.payback_period_months)} mo
                      </p>
                    </div>
                  </div>

                  <div className="space-y-2 pt-2 border-t border-green-500/20">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Annual Net Benefit</span>
                      <span className="text-sm font-bold text-green-600">
                        ₹{formatNumber(result.annual_savings.net_benefit)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Total Annual Savings</span>
                      <span className="text-sm font-bold">
                        ₹{formatNumber(result.annual_savings.total_savings)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Environmental Impact */}
              <Card className="border-2 border-emerald-500/20 bg-gradient-to-br from-emerald-500/5 to-transparent">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-emerald-600">
                    <Leaf className="w-5 h-5" />
                    Environmental Impact
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white/50 dark:bg-black/20 rounded-lg p-4 border border-emerald-500/20">
                      <p className="text-xs text-muted-foreground mb-1">CO₂ Reduction</p>
                      <p className="text-2xl font-bold text-emerald-600">
                        {formatNumber(result.environmental.co2_reduction_pct)}%
                      </p>
                    </div>
                    <div className="bg-white/50 dark:bg-black/20 rounded-lg p-4 border border-emerald-500/20">
                      <p className="text-xs text-muted-foreground mb-1">Trees Equivalent</p>
                      <p className="text-2xl font-bold text-emerald-600">
                        {formatNumber(result.environmental.trees_equivalent)}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-2 pt-2 border-t border-emerald-500/20">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">CO₂ Saved Annually</span>
                      <span className="text-sm font-bold text-emerald-600">
                        {formatNumber(result.annual_savings.co2_saved_kg)} kg
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Energy Saved Annually</span>
                      <span className="text-sm font-bold">
                        {formatNumber(result.annual_savings.energy_saved_kwh)} kWh
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Energy Efficiency Gain</span>
                      <span className="text-sm font-bold">
                        {formatNumber(result.environmental.energy_efficiency_improvement_pct)}%
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Operational Improvements */}
              <Card className="border-2 border-blue-500/20 bg-gradient-to-br from-blue-500/5 to-transparent">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-blue-600">
                    <TrendingUp className="w-5 h-5" />
                    Operational Improvements
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Quality Improvement</span>
                      <span className="text-sm font-bold text-blue-600">
                        +{formatNumber(result.improvements.quality_improvement_pct)}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Yield Improvement</span>
                      <span className="text-sm font-bold text-blue-600">
                        +{formatNumber(result.improvements.yield_improvement_pct)}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Performance Improvement</span>
                      <span className="text-sm font-bold text-blue-600">
                        +{formatNumber(result.improvements.performance_improvement_pct)}%
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="border-2 border-dashed border-muted">
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Factory className="w-16 h-16 text-muted-foreground/30 mb-4" />
                <p className="text-muted-foreground text-center">
                  Adjust parameters and click "Calculate Validation" to see results
                </p>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </div>

      {/* Detailed Breakdown */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6"
        >
          {/* Baseline vs Optimized */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Baseline Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableBody>
                  <TableRow>
                    <TableCell className="text-xs text-muted-foreground">Quality</TableCell>
                    <TableCell className="text-right text-sm font-medium">
                      {formatNumber(result.baseline.quality)}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="text-xs text-muted-foreground">Yield</TableCell>
                    <TableCell className="text-right text-sm font-medium">
                      {formatNumber(result.baseline.yield)}%
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="text-xs text-muted-foreground">Performance</TableCell>
                    <TableCell className="text-right text-sm font-medium">
                      {formatNumber(result.baseline.performance)}%
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="text-xs text-muted-foreground">Energy/Batch</TableCell>
                    <TableCell className="text-right text-sm font-medium">
                      {formatNumber(result.baseline.energy_per_batch)} kWh
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="text-xs text-muted-foreground">CO₂/Batch</TableCell>
                    <TableCell className="text-right text-sm font-medium">
                      {formatNumber(result.baseline.co2_per_batch)} kg
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Optimized Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableBody>
                  <TableRow>
                    <TableCell className="text-xs text-muted-foreground">Quality</TableCell>
                    <TableCell className="text-right text-sm font-medium text-green-600">
                      {formatNumber(result.optimized.quality)}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="text-xs text-muted-foreground">Yield</TableCell>
                    <TableCell className="text-right text-sm font-medium text-green-600">
                      {formatNumber(result.optimized.yield)}%
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="text-xs text-muted-foreground">Performance</TableCell>
                    <TableCell className="text-right text-sm font-medium text-green-600">
                      {formatNumber(result.optimized.performance)}%
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="text-xs text-muted-foreground">Energy/Batch</TableCell>
                    <TableCell className="text-right text-sm font-medium text-green-600">
                      {formatNumber(result.optimized.energy_per_batch)} kWh
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="text-xs text-muted-foreground">CO₂/Batch</TableCell>
                    <TableCell className="text-right text-sm font-medium text-green-600">
                      {formatNumber(result.optimized.co2_per_batch)} kg
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Annual Savings Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Annual Savings Breakdown</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableBody>
                  <TableRow>
                    <TableCell className="text-xs text-muted-foreground">Energy Savings</TableCell>
                    <TableCell className="text-right text-sm font-medium">
                      ₹{formatNumber(result.annual_savings.energy_cost_savings)}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="text-xs text-muted-foreground">Material Savings</TableCell>
                    <TableCell className="text-right text-sm font-medium">
                      ₹{formatNumber(result.annual_savings.raw_material_savings)}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="text-xs text-muted-foreground">Quality Savings</TableCell>
                    <TableCell className="text-right text-sm font-medium">
                      ₹{formatNumber(result.annual_savings.quality_savings)}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="text-xs text-muted-foreground">Performance Savings</TableCell>
                    <TableCell className="text-right text-sm font-medium">
                      ₹{formatNumber(result.annual_savings.performance_savings)}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="text-xs text-muted-foreground">Maintenance Cost</TableCell>
                    <TableCell className="text-right text-sm font-medium text-red-500">
                      -₹{formatNumber(result.inputs.annual_maintenance_cost)}
                    </TableCell>
                  </TableRow>
                  <TableRow className="border-t-2">
                    <TableCell className="text-xs font-bold">Net Annual Benefit</TableCell>
                    <TableCell className="text-right text-sm font-bold text-green-600">
                      ₹{formatNumber(result.annual_savings.net_benefit)}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  )
}

export default IndustrialValidation
