library(tidyverse)
library(lme4)
library(emmeans)
library(lsmeans)
library(lmerTest)
library(Cairo)
library(sjPlot)
library(scales)
CairoWin()

df <- read_csv("C:\\Users\\roryl\\repos\\context_analysis\\data\\pilot\\freezebyblock.csv")

df2 <- df %>%
  mutate(
    context = as.factor(context),
    Group = factor(Group, levels=c("No Shock", "One Context", "Experimental")),
  ) %>%
  rename(group=Group) %>%
  filter(context %in% c("safe", "danger"))

df2 %>%
  ggplot(aes(x=freeze)) +
  geom_histogram()


contrasts(df2$group) <- cbind("ns"=c(-2, 1, 1), "exp"=c(0, -1, 1))

mod1 <- lmerTest::lmer(freeze ~ (1 | mouse),data=df2)
mod2 <- lmerTest::lmer(freeze ~ block_number + context + group + session + context:group + (1 | mouse),data=df2)
anova(mod2)
summary(mod2)
AIC(mod2)


tab_model(mod1, mod2)
tab_model(mod2)

colors <- c(
  "Experimental"="#856ced",
  "No Shock"="#5c5c6c",
  "One Context"="#01011b"
)

em2 <- emmeans(mod2, pairwise ~ group)
df_em <- as_tibble(em2$emmeans)
df_em %>%
  ggplot(aes(x=group, y=emmean, color=group)) +
  geom_point() +
  geom_errorbar(aes(ymin=emmean-SE, ymax=emmean+SE), width=0.5) +
  labs(x="", y="Proportion Time Freezing") +
  scale_color_manual(values=colors) +
    theme_Publication() + 
  ggsave("groups.svg")

# em2


em3 <- emmeans(mod2, pairwise ~ context | group)
df_em <- as_tibble(em3$emmeans)
df_em %>%
  ggplot(aes(x=context, y=emmean, color=group)) +
  geom_point() +
  geom_errorbar(aes(ymin=emmean-SE, ymax=emmean+SE), width=0.5) +
  facet_grid(cols=vars(group)) +
  scale_color_manual(values=colors) +
  labs(x="", y="Proportion Time Freezing") +
  theme_Publication() + 
  ggsave("contrast.svg")


df_plot <- df2 %>%
  group_by(block_number, group, context, session) %>%
  summarize(loc=mean(freeze), se=sd(freeze)/sqrt(n()))

df_plot %>%
  filter(session == "day3-test1") %>%
  ggplot(aes(x=(block_number * 2) + 1, y=loc, group=group, color=group)) + 
    geom_line() +
    geom_point()+
    geom_errorbar(aes(ymin=loc+se, ymax=loc-se), width=.2,
                  position=position_dodge(0.05)) +
  lims(x=c(0, 12)) +
  ggtitle("Test 1") +
  labs(x="Time", y="Proportion Time Freezing") +
  scale_x_continuous(breaks=scales::pretty_breaks()) +
  scale_color_manual(values=colors) +
  theme_Publication()+
  ggsave("day3.svg")

df_plot %>%
  filter(session == "day4-test2") %>%
  ggplot(aes(x=(block_number * 2) + 1, y=loc, group=group, color=group)) + 
  geom_line(size=1) +
  geom_point()+
  geom_errorbar(aes(ymin=loc+se, ymax=loc-se), width=.2,
                position=position_dodge(0.05)) +
  theme_minimal() +
  ggtitle("Test 2") +
  labs(x="Time", y="Proportion Time Freezing") +
  lims(x=c(0, 12)) +
  scale_x_continuous(breaks=scales::pretty_breaks()) +
  scale_color_manual(values=colors) +
  theme_Publication()+
  ggsave("day4.svg", width=5.24, height=3.98)



df_plot %>% 
  mutate(t = block_number + 1)
