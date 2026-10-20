def is_owner(user_id: int):
    def predicate(ctx):
        return ctx.author.id == user_id
    return predicate


def is_guild():
    def predicate(ctx):
        return ctx.guild is not None
    return predicate


def is_dm():
    def predicate(ctx):
        return ctx.guild is None
    return predicate


def has_role(role_id: int):
    def predicate(ctx):
        if not ctx.guild:
            return False
        member = ctx.guild.get_member(ctx.author.id)
        return member and str(role_id) in member.roles
    return predicate


def has_any_role(*role_ids: int):
    def predicate(ctx):
        if not ctx.guild:
            return False
        member = ctx.guild.get_member(ctx.author.id)
        if not member:
            return False
        member_roles = set(member.roles)
        return any(str(role_id) in member_roles for role_id in role_ids)
    return predicate
