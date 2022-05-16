#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
import requests
import sys
from typing import Iterator, Union, cast

import cwl_utils.parser.cwl_v1_0 as cwl

ProcessType = Union[cwl.Workflow, cwl.CommandLineTool, cwl.ExpressionTool]


def main() -> int:
    """Load the first argument and extract the software requirements."""
    top = cwl.load_document(sys.argv[1])
    traverse(top)
    return 0


def extract_software_packages(process: ProcessType) -> None:
    """Print software packages found in the given process."""
    for req in extract_software_reqs(process):
        print(process.id)
        process_software_requirement(req)
        query_biotools(req) # added by Renske


def extract_software_reqs(
    process: ProcessType,
) -> Iterator[cwl.SoftwareRequirement]:
    """Return an iterator over any SoftwareRequirements found in the given process."""
    if process.requirements:
        for req in process.requirements:
            if isinstance(req, cwl.SoftwareRequirement):
                yield req
    if process.hints:
        for req in process.hints:
            if req["class"] == "SoftwareRequirement":
                yield cwl.load_field(
                    req,
                    cwl.SoftwareRequirementLoader,
                    process.id if process.id else "",
                    process.loadingOptions,
                )


def process_software_requirement(req: cwl.SoftwareRequirement) -> None:
    """Pretty print the software package information."""
    for package in req.packages:
        print(
            "Package: {}, version: {}, specs: {}".format(
                package.package, package.version, package.specs
            )
        )


def traverse(process: ProcessType) -> None:
    """Extract the software packages for this process, and any steps."""
    extract_software_packages(process)
    if isinstance(process, cwl.Workflow):
        traverse_workflow(process)


def get_process_from_step(step: cwl.WorkflowStep) -> ProcessType:
    """Return the process for this step, loading it if needed."""
    if isinstance(step.run, str):
        return cast(ProcessType, cwl.load_document(step.run))
    return cast(ProcessType, step.run)


def traverse_workflow(workflow: cwl.Workflow) -> None:
    """Iterate over the given workflow, extracting the software packages."""
    for step in workflow.steps:
        extract_software_packages(step)
        traverse(get_process_from_step(step))

## Added by Renske
def query_biotools(req):
    """Retrieve metadata from bio.tools."""
    for package in req.packages:
        for spec in package.specs:
            if "bio.tools" in spec:
                biotools_id = spec.split('/')[-1] # adapt for case where spec ends in /
                query = f"https://bio.tools/api/tool/{biotools_id}/?format=json"
                metadata = requests.get(query).json()
                print(extract_citation(metadata))

def extract_citation(json: dict) -> list:
    publication = json['publication'] # list

    for pub in publication:
        doi = []
        if 'Primary' in pub['type']:
            doi_id = f"https://doi.org/{pub['doi']}"
            doi.append(doi_id)

    return doi

if __name__ == "__main__":
    sys.exit(main())
