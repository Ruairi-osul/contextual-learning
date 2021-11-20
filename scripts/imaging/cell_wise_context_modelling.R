library(tidyverse)
library(lme4)
library(lmerTest)
library(arrow)
library(broom)
library(car)
library(emmeans)
library(ggeffects)

colors <- c(
  "Experimental" = "#856ced",
  "No Shock" = "#5c5c6c",
  "One Context" = "#01011b"
)
df <-
  arrow::read_feather(
    "C:\\Users\\roryl\\repos\\context_analysis\\data\\pfc\\derived\\spikes_by_block.f"
  )
df <-
  mutate(df, group = factor(group, levels = c("One Context", "No Shock", "Experimental")))
df <- rename(df, context = block)
df <- mutate(df, cell_id = factor(cell_id))


############# test 1

df1 <- filter(df, session_name == "day4-test1")
mod <-
  glmer(
    spiketimes ~ group * context + (1 + context |
                                      cell_id),
    data = df1,
    family = "poisson",
    control = glmerControl(optimizer = "bobyqa")
  )
summary(mod)
Anova(mod, type = "III")

groups_marginal <- emmeans(mod, pairwise ~ (context | group))
df_em <- as_tibble(groups_marginal$emmeans)
df_em %>%
  ggplot(aes(x = context, y = emmean, color = group)) +
  geom_point() +
  geom_errorbar(aes(ymin = emmean - SE, ymax = emmean + SE),
                width = 0.5,
                size = 1) +
  facet_grid(cols = vars(group)) +
  scale_color_manual(values = colors) +
  labs(x = "", y = "Marginal Effect on\nSpike Counts") +
  theme_Publication()
groups_marginal$contrasts
# interaction between group and group and context
fixed_effects <- fixef(mod)
fixed_effects
fe_one_context <- fixed_effects["contextscary"]
fe_no_shock <-
  fixed_effects["contextscary"] + (fixed_effects["groupNo Shock:contextscary"])
fe_exp <-
  fixed_effects["contextscary"] + (fixed_effects["groupExperimental:contextscary"])
fixed_effects <- tibble(
  fixed_effects = c(
    "One Context" = fe_one_context,
    "Experimental" = fe_exp,
    "No Shock" = fe_no_shock
  ),
  group = c("One Context", "Experimental", "No Shock")
)

df_d4 <- as_tibble(ranef(mod)) %>%
  rename(cell_id = grp) %>%
  rename(random_effects = condval) %>%
  filter(term == "contextscary") %>%
  select(cell_id, random_effects, condsd) %>%
  left_join(distinct(select(df, cell_id, group))) %>%
  left_join(fixed_effects) %>%
  mutate(slope_estimate = random_effects + fixed_effects) %>%
  arrange(slope_estimate) %>%
  group_by(group) %>%
  mutate(rank = order(slope_estimate, decreasing = TRUE))

ggplot(df_d4, aes(x = slope_estimate)) +
  geom_histogram(
    bins = 60,
    fill = "white",
    color = "black",
    size = 1
  ) +
  facet_grid(rows = vars(group), scales = "free") +
  theme_minimal() +
  geom_vline(aes(xintercept = fixed_effects),
             size = 2,
             color = "red") +
  lims(x = c(-1.2, 1.2)) +
  theme_Publication() +
  labs(y = "Marginal Effect of Shock-Associated\nContext on Spike Counts", x =
         "Regression Coeffcient")

################################# test2

df2 <- filter(df, session_name == "day5-test2")
mod <-
  glmer(
    spiketimes ~ group * context + (1 + context |
                                      cell_id),
    data = df2,
    family = "poisson",
    control = glmerControl(optimizer = "bobyqa")
  )
summary(mod)
Anova(mod, type = "III")
groups_marginal <- emmeans(mod, pairwise ~ (context | group))
df_em <- as_tibble(groups_marginal$emmeans)
df_em %>%
  ggplot(aes(x = context, y = emmean, color = group)) +
  geom_point() +
  geom_errorbar(aes(ymin = emmean - SE, ymax = emmean + SE),
                width = 0.5,
                size = 1) +
  facet_grid(cols = vars(group)) +
  scale_color_manual(values = colors) +
  labs(x = "", y = "Marginal Effect on\nSpike Counts") +
  theme_Publication()
groups_marginal$contrasts

fixed_effects <- fixef(mod)
fe_one_context <- fixed_effects["contextscary"]
fe_no_shock <-
  fixed_effects["contextscary"] + (fixed_effects["groupNo Shock:contextscary"])
fe_exp <-
  fixed_effects["contextscary"] + (fixed_effects["groupExperimental:contextscary"])
fixed_effects <-
  tibble(
    fixed_effects = c(
      "One Context" = fe_one_context,
      "Experimental" = fe_exp,
      "No Shock" = fe_no_shock
    ),
    group = c("One Context", "Experimental", "No Shock")
  )

df_d5 <- as_tibble(ranef(mod)) %>%
  rename(cell_id = grp) %>%
  rename(random_effects = condval) %>%
  filter(term == "contextscary") %>%
  select(cell_id, random_effects, condsd) %>%
  left_join(distinct(select(df, cell_id, group))) %>%
  left_join(fixed_effects) %>%
  mutate(slope_estimate = random_effects + fixed_effects) %>%
  arrange(slope_estimate) %>%
  group_by(group) %>%
  mutate(rank = order(slope_estimate, decreasing = TRUE))

ggplot(df_d5, aes(x = slope_estimate)) +
  geom_histogram(
    bins = 60,
    fill = "white",
    color = "black",
    size = 1
  ) +
  facet_grid(rows = vars(group), scales = "free") +
  theme_minimal() +
  geom_vline(aes(xintercept = fixed_effects),
             size = 2,
             color = "red") +
  lims(x = c(-1.2, 1.2)) +
  theme_Publication() +
  labs(y = "Marginal Effect of Shock-Associated\nContext on Spike Counts", x =
         "Regression Coeffcient")


######

df_res <- df1 %>%
  group_by(cell_id) %>%
  do(tidy(lm(spiketimes ~ context, data=., REML=F)))

df_res %>%
  filter(term=="contextscary") %>%
  mutate(p_adj = p.adjust(p.value)) %>%
  left_join(distinct(select(df, cell_id, group))) %>%
  group_by(group) %>%
  summarise(m = mean(p_adj < 0.05))
  
