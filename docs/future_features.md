---
title: Future Features
date: 20200910
author: Lyz
---

Design documentation for the features I'd love to create in the future.

# The game of life

The goal is to measure the user state to suggest which kind of task are more
suitable, raise alerts when the user reaches certain mental or physical states
or give insights on the evolution of the user attributes.

## Domain Model

### User model

We could model the state of a human with the following attributes groups:

* Mental attributes.
* Health attributes.
* Physical attributes.
* Skills.
* Traits.

I've still not figured out how to vary the total attribute values over the time.

#### Mental attributes

* Mental Energy: Measures the amount of mental work that you can do before
    getting fatigued.

* Vitality: Measures your life force of wanting to do things. For example, for
    me, dancing or doing work out is a task that increases my vitality, while
    staying in the couch for 5 hours watching tv shows kills my vitality.

* [Tranquility](https://en.wikipedia.org/wiki/Tranquillity): Measures the state
    of being calm, serene, and worry-free. As a side effect it measures the
    levels of stress and anxiety.

* [Mental load](https://www.mindbodygreen.com/articles/what-is-the-mental-load):
    Measure of the invisible labor involved in managing yourself, a household
    and your closed ones, which typically falls on women's shoulders. Also
    sometimes referred to as *worry work* or *cognitive labor*, the mental load
    is about not the physical tasks but rather the overseeing of those tasks.
    It's being the one in charge of having the never-ending list of to-do items
    constantly running in your head, remembering what needs to get done and
    when, delegating tasks to others, and making sure they actually get done.

    [One study](https://journals.sagepub.com/doi/10.1177/0003122419859007)
    describes it as the responsibility of *anticipating needs, identifying
    options for filling them, making decisions, and monitoring progress.*

* [Pleasure](https://en.wikipedia.org/wiki/Pleasure): Measures the broad class
    of mental states that we experience as positive, enjoyable, or worth seeking.
    It includes more specific states such as happiness, entertainment,
    enjoyment, ecstasy and euphoria.

* [Intelligence](https://en.wikipedia.org/wiki/Intelligence): Measures the
    capacity for logic, understanding, self-awareness, learning, emotional
    knowledge, reasoning, planning, creativity, critical thinking, and
    problem-solving. More generally, it's the ability to perceive or infer
    information, and to keep it as knowledge to be applied towards adaptive
    behaviors within an environment or context.

    * [Logic](https://en.wikipedia.org/wiki/Logic): Measures the systematic
        study of valid rules of inference, i.e. the relations that lead to the
        acceptance of one proposition (the conclusion) on the basis of a set of
        other propositions (premises). More broadly, logic is the analysis and
        appraisal of arguments.

    * [Understanding](https://en.wikipedia.org/wiki/Understanding): Measures the
        psychological process related to an abstract or physical object, such as
        a person, situation, or message whereby one is able to think about it
        and use concepts to deal adequately with that object. Understanding is
        a relation between the knower and an object of understanding.
        Understanding implies abilities and dispositions in relation to an
        object of knowledge that are enough to support intelligent
        behavior.

    * [Self-awareness](https://en.wikipedia.org/wiki/Self-awareness): Measures
        the experience of one's own personality or individuality. While
        consciousness is being aware of one's environment and body and
        lifestyle, self-awareness is the recognition of that awareness.
        Self-awareness is how an individual consciously knows and understands
        their own character, feelings, motives, and desires.

    * [Learning](https://en.wikipedia.org/wiki/Learning): Measures the process of
        acquiring new understanding, knowledge, behaviors, skills, values,
        attitudes, and preferences.

    * [Emotional
        Intelligence](https://en.wikipedia.org/wiki/Emotional_intelligence):
        Measures the ability of individuals to recognize their own emotions and
        those of others, discern between different feelings and label them
        appropriately, use emotional information to guide thinking and behavior,
        and manage and/or adjust emotions to adapt to environments or achieve
        one's goals.

    * [Reasoning](https://en.wikipedia.org/wiki/Reason): Measures the capacity
        of consciously making sense of things, applying logic, and adapting or
        justifying practices, institutions, and beliefs based on new or existing
        information. It's associated with such characteristically human
        activities as philosophy, science, language, mathematics, and art.
        Reason is sometimes referred to as rationality.

    * [Planning](https://en.wikipedia.org/wiki/Planning): Measures the process
        of thinking about the activities required to achieve a desired goal. It
        involves the creation and maintenance of a plan, such as psychological
        aspects that require conceptual skills.

    * [Creativity](https://en.wikipedia.org/wiki/Creativity): Measures the
        ability to create something new and somehow valuable. The created item
        may be intangible (such as an idea, a scientific theory, a musical
        composition, or a joke) or a physical object (such as an invention,
        a printed literary work, or a painting).

    * [Critical Thinking](https://en.wikipedia.org/wiki/Critical_thinking):
        Measures the analysis of facts to form a judgment. It's the rational,
        skeptical, unbiased analysis, or evaluation of facts.
        Critical thinking is self-directed, self-disciplined, self-monitored,
        and self-corrective thinking. It presupposes assent to rigorous
        standards of excellence and mindful command of their use. It entails
        effective communication and problem-solving abilities as well as
        a commitment to overcome native egocentrism and sociocentrism.

    * [Problem Solving](https://en.wikipedia.org/wiki/Problem_solving): Measure
        the ability to use generic or ad hoc methods in an orderly manner to
        find solutions to problems.

    * [Memory](https://en.wikipedia.org/wiki/Memory): Measures the faculty of
        the brain to encode, store and retrieve over the time data or
        information.

* [Self-control](https://en.wikipedia.org/wiki/Self-control): Measures the
    ability to regulate one's emotions, thoughts, and behavior in the face of
    temptations and impulses. As an executive function, self-control is
    a cognitive process that is necessary for regulating one's behavior in order
    to achieve specific goals.

    Self-regulation, whether emotional or behavioral, is a limited resource
    which functions like energy. In the short term, overuse of self-control will
    lead to depletion. In the long term, the use of self-control can strengthen
    and improve over time.

* [Social interaction](https://en.wikipedia.org/wiki/Social_relation): Measures
    the amount of relationship you can endure with other human beings.

* [Wisdom](https://en.wikipedia.org/wiki/Wisdom): Measures the ability to think
    and act using knowledge, experience, understanding, common sense and
    insight. It's associated with attributes such as unbiased judgment,
    compassion, experiential self-knowledge, self-transcendence and
    non-attachment, and virtues such as ethics and benevolence.

* [Charisma](https://en.wikipedia.org/wiki/Charisma): Measures the force of
    personality, persuasiveness and leadership.

#### Health attributes

[Health](https://en.wikipedia.org/wiki/Health) Measures the state of physical,
mental and social well-being in which disease and infirmity are absent.

Achieving and maintaining health is an ongoing process, shaped by both the
evolution of health care knowledge and practices as well as personal strategies
and organized interventions for staying healthy.

* [Diet](https://en.wikipedia.org/wiki/Healthy_diet): Measures how much does the
    food you eat follow a healthy diet. A healthy diet includes a variety of
    foods that provide the different nutrients required by your body to keep on
    running. Nutrients help build and strengthen bones, muscles, and tendons and
    also regulate body processes. Also remember that water consumption is
    essential.

* [Exercise](https://en.wikipedia.org/wiki/Exercise): Measures the amount of
    physical fitness. It strengthens muscles and improves the cardiovascular
    system.

* [Sleep](https://en.wikipedia.org/wiki/Sleep): Measures the quality of your
    rest. Sleep is an essential component to maintaining health. Ongoing sleep
    deprivation causes an increased risk for some chronic health problems. In
    addition, sleep deprivation correlates with both increased susceptibility to
    illness and slower recovery times from illness. Due to the role of sleep in
    regulating metabolism, insufficient sleep may also play a role in weight
    gain.

* [Social Support](https://en.wikipedia.org/wiki/Social_support): Measures the
    perception and actuality that one is cared for, has assistance available
    from other people, and that one is part of a supportive social network.
    Support can come from diverse sources, such as family, friends, pets,
    neighbors, coworkers, organizations, etc.

    There are four common functions of social support:

    * *Emotional support*: Measures the offering of empathy, concern, affection,
        love, trust, acceptance, intimacy, encouragement, or caring. It's the
        warmth and nurturance provided by sources of social support. Providing
        emotional support can let the individual know that they are valued.

    * *Tangible support*: Measures the provision of financial help, material
        goods, or services. Also called instrumental support, this form of
        social support encompasses the concrete, direct ways people assist
        others.

    * *Informational support*: Measures the provision of advice, guidance,
        suggestions, or useful information to someone. Where this information
        has the potential to help others problem-solve.

    * *Companionship support*: Measures the support that gives someone a sense
        of social belonging, the presence of companions to engage in shared
        social activities. It's also referred to as *esteem support* or
        *appraisal support*.

* [Cleanliness](https://en.wikipedia.org/wiki/Cleanliness): Measures both the
    abstract state of being clean and free from germs, dirt, trash, or waste,
    and the habit of achieving and maintaining that state.

    * [Hygiene](https://en.wikipedia.org/wiki/Hygiene): Measures the conditions
        and practices that help to maintain health and prevent the spread of
        diseases. It includes such personal habit choices as how frequently to
        take a shower or bath, wash hands, trim fingernails, and wash clothes.
        It also includes attention to keeping surfaces in the home and workplace
        clean and pathogen-free.

    * [Tidyness](https://dictionary.cambridge.org/dictionary/english/tidiness):
        Measures the condition or quality of having everything ordered and
        arranged in the right place.

#### Physical attributes

* Physical Energy: Measures the amount of physical work that you can do before
    getting fatigued.

* [Strength](https://en.wikipedia.org/wiki/Physical_strength): Measures the
    exertion of force on physical objects.

* Dexterity: Measuring agility, balance, accuracy, speed, coordination and
    reflexes.

#### Skills

[Skills](https://en.wikipedia.org/wiki/Skill) are the abilities to perform an
action with determined results within a given amount of time or energy. Skills
are divided into domain-general and domain-specific skills. For example, in the
domain of work, some general skills would include time management, teamwork and
leadership, self-motivation and others, whereas domain-specific skills would be
used only for a certain job.

Skills [can be categorized based on the level of expertise and
motivation](https://en.wikipedia.org/wiki/File:KokcharovSkillHierarchy2015.jpg)
in different phases:

* *Student*: Get the basic knowledge required to start performing the skill.
* *Apprentice*: Use the basic knowledge following specified instructions.
* *Specialist*: Use the state of the art knowledge following specified instructions.
* *Expert*: Creatively use the knowledge to resolve problems defining new
    instructions.
* *Craftsman*: Create new knowledge, skills, products or services.

We can use a skill tree to track the evolution and visualize the dependencies
between them.

We can model skill decay with pattern like the space repetition, so it's cheaper
to relearn, and will increase of the percent you don't forget.

#### States

States are conditions derived by the combination of user attribute levels. They
can be used to increase or decrease the rate of consumption/gain of other user
attributes. For example if you are tired, you can loose energy more quickly.

* Emotional states.
* Mental states.
* Physical states.
* Health states.

#### Traits

[Traits](https://en.wikipedia.org/wiki/Trait_theory) are habitual patterns of
behavior, thought, and emotion that define our personality. They are stable over
time, differ across individuals, are consistent over situations, and influence
behavior. Traits are in contrast to states, which are more transitory
dispositions.

People at the MIT have gathered a [list of different
traits](http://ideonomy.mit.edu/essays/traits.html).

We could use traits to let the user define themselves, using it as a modifier of
their attributes in contrast of what they read as *normal*. For example, If the
user thinks they are forgetful, they will have a penalty of -X in the Memory
attribute.

### Task model

A task is an activity performed to achieve a goal. The process of doing a task
costs us time and consumption of user attributes. In exchange, we get other
user attributes and the partial or total solving of the issue.

The task attributes are:

* Time: Measures the amount of time required to perform the task.
    * Estimated: Measures the amount of time we think we need to do the task.
    * Real: Measures the real time it took us to perform the task.

* [Effectiveness](https://en.wikipedia.org/wiki/Effectiveness): Measures the
    capability of solving the issue. For example we could use the following
    scale:

    * *5*: Fully solve the problem in a way that it doesn't happen again.
    * *4*: Fully Solves part of the problem in a way that it doesn't happen
        again.
    * *3*: Temporarily solves the problem for a long period of time.
    * *2*: Temporarily solves part of the problem for a long period of time.
    * *1*: Temporarily solves the problem for a short period of time.

* Attribute Cost/Gain: List of user attributes that gets consumed or obtained
    while doing the task. The total cost/gain will be calculated as the integral
    of these attributes over the time.

#### Actions

Actions are task templates, they are meant to reduce the user attribute
management in the tasks.

They are defined by group of words and gather a default value of task attributes
like consumed/gained attributes, project, tags and associated skills.

For example, shuffle dancing, identified by the words `dance shuffle` can have
the following attributes:

* Priority: 2
* Estimate: 1
* Physical Energy: -5
* Mental Energy: +2
* Vitality: +4
* Tranquility: +3
* Pleasure: +4
* Creativity: +3
* Exercise: +3
* Dexterity: +2

The following skills:

* Dancing: Apprentice
* Shuffle dancing: Apprentice

And belong to the project `dance`.

Then in the future you'll only need to write `pydo add dance shuffle in the
park`. And all the attributes will be filled for you.

### Problem model

[Problems](https://dictionary.cambridge.org/dictionary/english/problem) in the
context of task management, are situations that need attention and to be solved.

Problems are solved by behaviours and tasks.

Problems can be grouped through projects or tags. The tasks and behaviours
related to solving the problem will inherit them.

They will have the following attributes:

* Value: Measures the degree of importance of the problem.
* Priority: Measures the need to be solved earlier compared to other problems.

We can model the negative effect they produce over the user by globally
subtracting user attribute points or by modifying the consumption rate of these
attributes associating them to states. The amount of the effect can be
a function of the overdue, priority and value. The decay will start decreasing
the user attributes in polinomic or exponential rate. This way we could
implement a soft recurrence, as we would have a repeating task without
recurrence, that will get automatically priorized due to the issue overdue, but
it won't appear in the overdue task list.

They can have a recurrence of type recurring or repeating.

### Behaviour model

Behaviours define the ways of acting. Tasks on the other hand define the actions
to achieve a goal. So dancing three times a week would be a behaviour and dance
in the park would be the task.

Behaviours once implemented solve problems with a low consumption of
self-control, mental load or physical and mental energy.

Behaviours don't affect user attributes, but can spawn tasks that do.

We'll aim to have a user friendly interface to keep on track of behaviours you
want to adopt or remove.

There will be a priorized list of behaviours that can be linked to projects and
tags.

There could be an interactive command line interface to answer at the start
and/or end of the day to keep track of the evolution of them.

Some behaviours can be linked to tasks, so once one is started, a popup is shown
with the behaviours that you want to change, once the task is completed it will
ask you if you've followed the behaviour or not.

## How does the system work

The user will give each task the gained/consumed user attribute values either
manually or through actions. While the tasks are active and at time of
completion in case they weren't activated, the integral of those attributes will
be added or removed from the global user attributes.

Certain states will be defined to be activated when specific attribute levels
are met. These states will change the consumption or gain of attributes while
they are active.

Based on the current user state, tasks will be or not recommended.

At anytime it can assess the attributes of the remaining tasks for the day to
see if its possible to achieve them, if they are not, recommend other tasks that
can improve the attribute that is making it impossible or suggest to reschedule
the least important tasks.

### Sleeping

The first time the program is executed in the day, it could ask you how well
and how much you've slept. Sleeping is one of the main sources of restoration.
Based in the answer, we will receive a different states can be defined to affect
the ratios of consumption/gain and total attribute levels.

We could take the baseline of sleeping well (value: 3) for 8 hours as a state without
buffs and a recovery of the 100% of the attributes.

If we've slept 8 hours but really well (value: 5), we could get the state of
*rested* which can give a temporal buff of more mental and physical energy. If
instead we've badly (value: 2) slept 5 hours we'd recover only the 42% of the
attributes the sleep resets (5*2/8*3) and get the *tired* state which increases
the consumption of energy.

# Make the task tracking easier

Tracking the active tasks is difficult and tedious, we need to make it user
friendly. Some ideas to achieve it could be:

* Have a command that stops tracking all the tasks when the user blocks
    the screen, and opens a pop-up that allows with a keystroke to keep on
    working on the previous task.
* Keep track of the context switches, so if a task has been active for 2 hours,
    it will ask the user if they are still working on the task, and to get
    a rest.
* Track the focus on windows to extract what are you doing. Or at least that
    when we open a specific program, it will automatically start tracking the
    related task. The idea would be to implement it through aliases in the
    terminal.

Tracking the unentered tasks can also be difficult. To make it easier we could:

* When there is a big period of untracked time, ask the user what did he do in
    that time. This can be done at the start or end of the day so as not to be
    too invasive.
* We could have a REPL interface to easily fill untracked times. With
    suggestions of common tasks completed in that time.

# Welcome and Goodbye reports

We could have a welcome report that shows the tasks to be done in the day, with
a timeline of the ones that have an due with hour and minute, and a priorized
list of the others.

We could have a goodbye report that asks your evaluation of the day, behaviours
questions, and shows you tomorrow's tasks.

# Refactor the task model into problem solving model

The idea is to drive your task priorization through the priorization of the
problems you want to solve.

The workflow would be to define a problem, and then the tasks and behaviours to
solve it.

The advantages of this model shift can be:

* The change in the priority of the problems, can affect a group of related
    tasks and behaviours thus helping in the planning.
* We can measure the cost of attributes of different solutions. For example if
    we had the problem of keeping the dishes clean, we could compare the task
    washing them manually and using the washing machine.
* Can be an help in auto assigning task attributes.

And the following disadvantages:

* It adds a management overload, because we'll need to create two resources
    (problem and solving entity) instead of just one.

The disadvantages can be solved with a user friendly REPL interface.

# Support tasks triggers

Create triggers for task creation and completion to be able to:

* Support external hooks.
* Affect states.
* Affect behaviours.
* Program chained tasks.

# Support flexible due date for tasks

Create a flexible due, where you specify the range of time around the due
date where the task can be completed.

# Add a REPL interface

Create a REPL interface to manage tasks in a way that:

* We see the entities that match a specified filter (i.e actionable tasks or
    problems).
* By default shows the state indicator, id and description. The state indicator
    will be one of the following:
    * `[ ]`: Open entity.
    * `[x]`: Done entity.
    * `[D]`: Deleted entity.
    * `[B]`: Blocked entity.
* With *j* and *k* you are able to navigate between them, *zo* and *zc* will be
    used to show/hide the entity attributes and children.
* *<<* and *>>* will make a task the sibling or child of the one above it.
* *d* will complete the task, *D* will delete it, *o* will reopen it.
* *b* will block it, then will ask the user for the reason.
* *a* will create a sibling task, *s* will create a subtask.
* *e* will launch an editor interface to change the entity attributes.

Create a REPL interface to add a task:

* Will prompt for the description, once entered it will try to automatically
    fill up the rest of attributes through actions or the related problem.
* Will show the generated attributes. And ask the user which attributes they
    want to edit. Acting differently on the keyboard events:
    * *enter*: Create the task as is.
    * *t*: launch the tag edition REPL interface:
        * *a*: Ask the user for the tags to introduce, with fuzzy auto
            suggestion and auto completion. If the tag doesn't exist suggest
            similar existing tags, if none exist or the user doesn't want them,
            ask if they are sure to add a new tag.
        * *j* and *k*: Navigate over the existing tags.
        * *d*: Delete the selected tag.
    * *p*: Launch the project edition REPL interface like the tag REPL interface
        above.
    * Define bindings for the rest of the attributes, perform input validation
        afterwards.

# Monica support

Connect pydo to [Monica](https://www.monicahq.com/) with the idea of linking
Monica activities and phone calls with pydo tasks.

# Context support

Create a way to be able to define which entities belong to a context or another
like *work* or *personal*, and once active it will only show the entities of
that context.
