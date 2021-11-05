from dash import html
from .citation import href

about = html.Div(
    className="content mb-5",
    children=[
        html.H4(className="title titleText", children="Overview"),
        html.P(
            children="""
            Using this website, you can explore the effects of a single 
            release of gene drive mosquitoes with different values of 
            various gene drive system and vector population parameters 
            on malaria elimination probabilities and prevalence, as well 
            as vector populations and genetics. Eight year-long simulations 
            of population replacement gene drive mosquito release were run 
            using EMOD 2.20 in a highly seasonal Sahelian setting over a 
            300 square kilometer region. Here elimination is defined as 
            occurring when malaria prevalence reaches zero by the end of 
            simulation year 7 and remains at zero through the end of simulation 
            year 8 across the entire spatial region.
            """
        ),
        html.P(
            children=[
                html.Span(
                    children="The parameters that can be explored here include the following:"
                ),
                html.Ul(
                    children=[
                        html.Li(
                            children="The probability of copying over the driver and/or "
                                     "effector genes when the driver gene is present (also "
                                     "known as drive efficiency; d in the classic case, d1 "
                                     "in the integral case)"
                        ),
                        html.Li(
                            children="The ability of the introduced effector gene to suppress "
                                     "malaria transmission in mosquitoes (also known as the "
                                     "transmission-blocking effectiveness of the drive, rc)"
                        ),
                        html.Li(
                            children="The pre-exsisting frequency of target site resistant alleles "
                                     "in the population (rr0 in the classic case, rr20 at the "
                                     "effector target site in the integral case)"
                        ),
                        html.Li(
                            children="The fitness cost associated with expressing the introduced "
                                     "driver and effector genes, represented by an increase in "
                                     "vector mortality (sne in the classic case, se2 associated "
                                     "with the effector in the integral case)."
                        )
                    ]
                )
            ]
        ),
        html.P(
            children=[
                html.Span(
                    children="The paper associated with these visualizations and results can be found "
                ),
                html.A(
                    href=href,
                    target="_blank",
                    children="here. "
                ),
                html.Span(
                    children="Any questions can be sen to "
                ),
                html.A(
                    href="mailto:support@idmod.org",
                    children="support@idmod.org"
                ),
                html.Span(".")

            ]
        ),
        html.H4(className="title titleText", children="Motivation"),
        html.P(
            children="""
                    Malaria remains a significant health burden in Sub-Saharan Africa 
                    (SSA) despite many decades of effort to eliminate the disease. 
                    However, concerns about drug and insecticide resistance threaten 
                    to stall traditional malaria control efforts. New strategies and 
                    technologies will therefore be needed to achieve elimination in 
                    SSA. Releases of gene drive mosquitoes are one potentially 
                    low-cost, long-lasting, and effective new strategy. Mosquitoes 
                    engineered with gene drive systems can copy specified genes from 
                    one chromosome to another in germline cells, ensuring that these 
                    genes are passed onto their offspring at higher than Mendelian 
                    inheritance rates and therefore rapidly spread through a population 
                    even if there are associated fitness costs.
                    """
        ),
        html.H4(className="title titleText", children="Gene Drive System Details"),
        html.P(
            children="""    
                    The homing endonuclease gene drive systems considered here consist 
                    of a driver gene that enables the copying of both itself and an 
                    “effector” gene, which in turn confers desired phenotypic traits. 
                    The driver gene encodes a guide RNA and an endonuclease, such as 
                    Cas9, that together recognize and cut specified DNA sequences 
                    present in the wildtype mosquito population. Within mosquitoes 
                    that are heterozygous in wildtype and drive or effector alleles, 
                    the cut wildtype chromosome uses its intact drive or 
                    effector-containing sister chromosome as a template for repairing 
                    itself, copying over the intact chromosome’s drive or 
                    effector-containing DNA in the process through homology-directed 
                    repair (HDR).
                    """
        ),
        html.P(
            children="""
                    Depending on which effector genes are introduced, gene drive mosquito 
                    releases can either reduce (population suppression) or modify 
                    (population replacement) a given vector population. Population 
                    replacement rather than suppression may be desirable in locations 
                    where the ecological effects of removing a mosquito species are not 
                    well known. For population replacement applied to malaria reduction 
                    or elimination, many potential effector genes have been shown to 
                    prevent malaria infection and/or transmission in Anopheles mosquitoes. 
                    These include genes that code for immune system activators, peptides 
                    that neutralize Falciparum parasites in the mosquito midgut or salivary 
                    glands, and others. We focus on population replacement strategies here.
                    """
        ),
        html.H4(className="title titleText",
                children="Important Gene Drive System and Vector Population Parameters to Explore"
        ),
        html.P(
            children="""
                    An important question that arises is how well effector genes must work in 
                    order to deliver substantial reductions in malaria transmission. 
                    Even without perfect blocking of malaria transmission within each engineered 
                    mosquito, can elimination be achieved? If there are significant fitness 
                    costs associated with expressing the effector, will it still be able to 
                    spread quickly through the population? Questions also arise around the 
                    required efficiency of the driver gene and gene drive system itself to 
                    achieve elimination. The process of copying the effector gene from one 
                    chromosome to another is not always successful. After cutting, DNA can 
                    sometimes undergo alternative repair pathways that do not result in 
                    accurate copying of the drive or effector-containing DNA on the sister 
                    chromosome, potentially generating “resistant” alleles that do not 
                    contain the desired drive or effector gene but are no longer recognized 
                    by the driver endonuclease. These resistant alleles may also be present 
                    in the wild mosquito population even before introduction of new drive or 
                    effector genes. The extent to which the generation and initial presence 
                    of these resistant alleles affects the ability of introduced genes to spread 
                    through the population via gene drive must be better quantified.
                    """
        )

    ])
