#This is a Nipype generator. Warning, here be dragons.
#!/usr/bin/env python

import sys
import nipype
import nipype.pipeline as pe

import nipype.interfaces.utility as utility
import nipype.interfaces.io as io
import nipype.interfaces.fsl as fsl
import nipype.interfaces.spm as spm

#Basic interface class generates identity mappings
utility_IdentityInterface = pe.Node(utility.IdentityInterface(fields=["subject", "run"]), name='utility_IdentityInterface')
utility_IdentityInterface.inputs.subject = ['01', '02', '03']
utility_IdentityInterface.inputs.run = [1, 2]

#Flexibly collect data from disk to feed into workflows.
io_SelectFiles = pe.MapNode(io.SelectFiles(templates={'anatomical':'Subject{subj_id}/Anatomical/anat.nii.gz','functional':'Subject{subj_id}/Functional/rEP3D_Session*.nii'}), name='io_SelectFiles')
io_SelectFiles.inputs.base_directory = '/project/3015003.04/FamTutorial/SubjectData/'
io_SelectFiles.inputs.anatomical = 'Subject{subj_id}/Anatomical/anat.nii.gz'
io_SelectFiles.inputs.functional = 'Subject{subj_id}/Functional/rEP3D_Session*.nii'

#Wraps the executable command ``bet``.
fsl_BET = pe.Node(interface = fsl.BET(), name='fsl_BET')

#Use spm_realign for estimating within modality rigid body alignment
spm_Realign = pe.Node(interface = spm.Realign(), name='spm_Realign')

#Wraps the executable command ``flirt``.
fsl_FLIRT = pe.Node(interface = fsl.FLIRT(), name='fsl_FLIRT')

#Create a workflow to connect all those nodes
analysisflow = nipype.Workflow('MyWorkflow')
analysisflow.connect(io_SelectFiles, "functional", spm_Realign, "in_files")
analysisflow.connect(io_SelectFiles, "anatomical", fsl_BET, "in_file")
analysisflow.connect(utility_IdentityInterface, "subject", io_SelectFiles, "subj_id")
analysisflow.connect(fsl_BET, "out_file", fsl_FLIRT, "in_file")
analysisflow.connect(spm_Realign, "mean_image", fsl_FLIRT, "reference")

#Run the workflow
plugin = 'MultiProc' #adjust your desired plugin here
plugin_args = {'n_procs': 1} #adjust to your number of cores
analysisflow.write_graph(graph2use='flat', format='png', simple_form=False)
analysisflow.run(plugin=plugin, plugin_args=plugin_args)
