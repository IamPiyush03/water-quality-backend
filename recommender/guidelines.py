"""WHO Guidelines for Water Quality Parameters"""

GUIDELINES = {
    "temperature": {
        "range": [20, 25],
        "severity_levels": {
            "mild": 28,
            "moderate": 30,
            "severe": 32,
            "critical": 35
        },
        "measures": {
            "high": {
                "immediate": [
                    "Implement emergency cooling measures. Monitor temperature every 15 minutes.",
                    "Increase aeration to enhance heat dissipation. Monitor DO levels during process.",
                    "Reduce thermal loading if possible. Implement temporary flow adjustments."
                ],
                "short_term": [
                    "Install temperature control system with automated monitoring. Include backup systems.",
                    "Implement comprehensive temperature monitoring network. Include real-time alerts.",
                    "Establish standard operating procedures for high temperature conditions."
                ],
                "long_term": [
                    "Conduct thermal impact assessment. Include climate change considerations.",
                    "Review and optimize temperature control systems. Consider advanced technologies.",
                    "Develop thermal management plan. Include source water protection strategies."
                ],
                "preventive": [
                    "Implement routine temperature monitoring. Maintain detailed records.",
                    "Establish maintenance schedule for cooling systems. Include regular inspection.",
                    "Develop emergency response plan for temperature excursions."
                ]
            }
        }
    },
    "dissolved_oxygen": {
        "range": [5.0, 8.0],
        "severity_levels": {
            "mild": 4.0,
            "moderate": 3.0,
            "severe": 2.0,
            "critical": 1.0
        },
        "measures": {
            "low": {
                "immediate": [
                    "Increase mechanical aeration in treatment process. Monitor DO levels every 15 minutes until stable.",
                    "Implement oxygen injection through diffusers or venturi systems. Monitor system performance.",
                    "Reduce organic loading in treatment process. Implement temporary flow reduction if necessary."
                ],
                "short_term": [
                    "Install high-efficiency aeration system with automated controls. Include backup power supply.",
                    "Implement comprehensive DO monitoring network with real-time data transmission.",
                    "Establish standard operating procedures for low DO conditions."
                ],
                "long_term": [
                    "Conduct comprehensive assessment of treatment process efficiency.",
                    "Review and optimize aeration system design. Consider advanced technologies.",
                    "Develop source water protection plan focusing on organic matter reduction."
                ],
                "preventive": [
                    "Implement routine DO monitoring with automated systems.",
                    "Establish maintenance schedule for aeration equipment.",
                    "Develop emergency response plan for low DO conditions."
                ]
            }
        }
    },
    "ph": {
        "range": [6.5, 8.5],
        "severity_levels": {
            "mild": 6.0,
            "moderate": 5.5,
            "severe": 5.0,
            "critical": 4.5
        },
        "measures": {
            "low": {
                "immediate": [
                    "Add calcium carbonate (CaCO3) at a rate of 10-20 mg/L to raise pH to acceptable range. Monitor pH every 15 minutes until stable.",
                    "Implement lime (Ca(OH)2) dosing at a rate of 5-10 mg/L with continuous pH monitoring. Adjust dosage based on real-time measurements.",
                    "Increase aeration to enhance CO2 stripping and raise pH naturally. Monitor dissolved oxygen levels during aeration."
                ],
                "short_term": [
                    "Install automated pH adjustment system with continuous monitoring and feedback control. System should include redundant pH probes and automatic calibration.",
                    "Implement comprehensive water quality monitoring system with remote alerts for pH deviations. Include backup power supply and data logging.",
                    "Establish standard operating procedures for pH adjustment including safety protocols, chemical handling, and emergency response."
                ],
                "long_term": [
                    "Conduct comprehensive water source assessment to identify causes of low pH. Include geological survey and historical water quality data analysis.",
                    "Review and optimize entire water treatment process. Consider implementing advanced treatment technologies like membrane filtration or ion exchange.",
                    "Develop source water protection plan to prevent pH fluctuations. Include watershed management and pollution prevention strategies."
                ],
                "preventive": [
                    "Implement routine pH monitoring schedule with automated sampling and analysis. Maintain detailed records for trend analysis.",
                    "Establish chemical storage and handling protocols following OSHA and EPA guidelines. Include regular safety training and equipment maintenance.",
                    "Develop emergency response plan for pH excursions. Include communication protocols, decision trees, and stakeholder notification procedures."
                ]
            },
            "high": {
                "immediate": [
                    "Add carbon dioxide (CO2) at a rate of 5-10 mg/L with continuous pH monitoring. Use food-grade CO2 and ensure proper ventilation.",
                    "Implement acid dosing (e.g., sulfuric acid) at a rate of 2-5 mg/L with automated control. Follow strict safety protocols for acid handling.",
                    "Increase aeration to enhance CO2 absorption and lower pH naturally. Monitor dissolved oxygen and pH simultaneously."
                ],
                "short_term": [
                    "Install automated pH adjustment system with redundant controls and safety interlocks. Include emergency shutdown procedures.",
                    "Implement comprehensive water quality monitoring network with real-time data transmission and automated alerts.",
                    "Establish standard operating procedures for high pH conditions including chemical handling, safety measures, and emergency response."
                ],
                "long_term": [
                    "Conduct source water assessment to identify causes of high pH. Include geological and hydrological studies.",
                    "Review and optimize water treatment process. Consider implementing advanced treatment technologies.",
                    "Develop source water protection plan focusing on pH stability. Include watershed management and pollution prevention."
                ],
                "preventive": [
                    "Implement routine pH monitoring with automated systems and manual verification. Maintain comprehensive records for analysis.",
                    "Establish chemical storage and handling protocols following regulatory requirements. Include regular safety audits.",
                    "Develop emergency response plan for pH excursions. Include communication protocols and stakeholder notification procedures."
                ]
            }
        }
    },
    "conductivity": {
        "range": [200, 800],
        "severity_levels": {
            "mild": 1000,
            "moderate": 1200,
            "severe": 1500,
            "critical": 2000
        },
        "measures": {
            "high": {
                "immediate": [
                    "Implement emergency dilution with low-conductivity water source. Monitor conductivity continuously during dilution process.",
                    "Activate emergency desalination system. Monitor system performance and adjust parameters based on real-time measurements.",
                    "Reduce industrial or agricultural discharges if identified as source. Implement temporary discharge restrictions."
                ],
                "short_term": [
                    "Install reverse osmosis system with pre-treatment and post-treatment monitoring. Include automatic flushing and cleaning cycles.",
                    "Implement ion exchange system with continuous monitoring. Include regeneration protocols and waste management procedures.",
                    "Establish standard operating procedures for high conductivity conditions. Include emergency response protocols."
                ],
                "long_term": [
                    "Conduct comprehensive source water assessment. Include geological survey and historical water quality analysis.",
                    "Review and optimize water treatment process. Consider implementing advanced treatment technologies.",
                    "Develop source water protection plan focusing on conductivity control. Include watershed management strategies."
                ],
                "preventive": [
                    "Implement routine conductivity monitoring with automated systems. Maintain comprehensive records for analysis.",
                    "Establish maintenance schedule for treatment systems. Include regular inspection and performance testing.",
                    "Develop emergency response plan for high conductivity conditions. Include communication protocols and stakeholder notification."
                ]
            }
        }
    },
    "bod": {
        "range": [0, 3],
        "severity_levels": {
            "mild": 5,
            "moderate": 8,
            "severe": 12,
            "critical": 15
        },
        "measures": {
            "high": {
                "immediate": [
                    "Increase aeration rate in treatment process. Monitor DO levels and adjust aeration accordingly.",
                    "Add supplemental biological treatment. Monitor system performance and adjust parameters as needed.",
                    "Implement temporary flow reduction if necessary. Monitor BOD levels during adjustment period."
                ],
                "short_term": [
                    "Install advanced biological treatment system with automated controls. Include backup systems.",
                    "Implement activated sludge process with comprehensive monitoring.",
                    "Establish standard operating procedures for high BOD conditions."
                ],
                "long_term": [
                    "Conduct comprehensive assessment of wastewater treatment process.",
                    "Review and optimize biological treatment system. Consider advanced technologies.",
                    "Develop source control program focusing on BOD reduction."
                ],
                "preventive": [
                    "Implement routine BOD monitoring with automated systems.",
                    "Establish maintenance schedule for treatment systems.",
                    "Develop emergency response plan for high BOD conditions."
                ]
            }
        }
    },
    "nitrate": {
        "range": [0, 10],
        "severity_levels": {
            "mild": 20,
            "moderate": 30,
            "severe": 40,
            "critical": 50
        },
        "measures": {
            "high": {
                "immediate": [
                    "Implement emergency dilution with low-nitrate water source. Monitor nitrate levels continuously during process.",
                    "Activate emergency nitrate removal system. Monitor system performance and adjust parameters as needed.",
                    "Implement temporary restrictions on fertilizer use in affected areas. Monitor nitrate levels during restriction period."
                ],
                "short_term": [
                    "Install ion exchange system with comprehensive monitoring. Include regeneration protocols and waste management.",
                    "Implement reverse osmosis system with pre-treatment. Include automatic flushing and cleaning cycles.",
                    "Establish standard operating procedures for high nitrate conditions. Include safety measures and emergency response."
                ],
                "long_term": [
                    "Conduct comprehensive assessment of nitrate sources. Include agricultural practices and land use analysis.",
                    "Review and optimize nitrate removal process. Consider implementing advanced treatment technologies.",
                    "Develop agricultural best management practices program. Include fertilizer management and conservation measures."
                ],
                "preventive": [
                    "Implement routine nitrate monitoring with automated systems. Maintain comprehensive records for analysis.",
                    "Establish fertilizer management program. Include application timing and rate guidelines.",
                    "Develop emergency response plan for high nitrate conditions. Include communication protocols and stakeholder notification."
                ]
            }
        }
    },
    "fecal_coliform": {
        "range": [0, 100],
        "severity_levels": {
            "mild": 200,
            "moderate": 500,
            "severe": 1000,
            "critical": 2000
        },
        "measures": {
            "high": {
                "immediate": [
                    "Implement emergency disinfection with increased chlorine dosage. Monitor residual chlorine levels.",
                    "Activate UV disinfection system at maximum intensity. Monitor UV transmittance.",
                    "Issue boil water advisory if necessary. Implement public notification procedures."
                ],
                "short_term": [
                    "Install advanced disinfection system with redundant controls.",
                    "Implement comprehensive microbial monitoring program.",
                    "Establish standard operating procedures for high coliform conditions."
                ],
                "long_term": [
                    "Conduct sanitary survey to identify contamination sources.",
                    "Review and optimize disinfection process. Consider advanced technologies.",
                    "Develop source water protection plan focusing on microbial control."
                ],
                "preventive": [
                    "Implement routine coliform monitoring with automated systems.",
                    "Establish maintenance schedule for disinfection systems.",
                    "Develop emergency response plan for microbial contamination."
                ]
            }
        }
    },
    "total_coliform": {
        "range": [0, 200],
        "severity_levels": {
            "mild": 500,
            "moderate": 1000,
            "severe": 2000,
            "critical": 5000
        },
        "measures": {
            "high": {
                "immediate": [
                    "Increase disinfection dosage with continuous monitoring. Adjust based on residual measurements.",
                    "Implement emergency filtration measures. Monitor turbidity and filter performance.",
                    "Issue public health advisory if necessary. Follow notification procedures."
                ],
                "short_term": [
                    "Install multi-barrier disinfection system. Include redundant treatment processes.",
                    "Implement comprehensive water quality monitoring program.",
                    "Establish standard operating procedures for contamination events."
                ],
                "long_term": [
                    "Conduct system-wide assessment of treatment barriers.",
                    "Review and optimize treatment train. Consider advanced technologies.",
                    "Develop watershed protection program. Include stakeholder engagement."
                ],
                "preventive": [
                    "Implement routine monitoring program with automated sampling.",
                    "Establish maintenance schedule for treatment systems.",
                    "Develop emergency response plan for contamination events."
                ]
            }
        }
    }
} 