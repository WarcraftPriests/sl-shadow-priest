function()
    local insanityGain = 0;
    -- SPELL_POWER_SHADOW_ORBS changes to mana in soulshape
    local currentInsanity = UnitPower("player", 13, forceUpdate);
    local maxInsanity = UnitPowerMax("player", 13);
    local currentSpell = UnitCastingInfo('player');
    local specGroup = GetActiveSpecGroup();
    local isFotMSelected = select(4, GetTalentInfo(1, 1, specGroup));
    local S2MName = select(2, GetTalentInfo(7, 3, specGroup));
    local isS2MActive = select(11, WA_GetUnitBuff("player", S2MName));
    
    if currentSpell == nil then
        insanityGain = 0;
        return 0,0,0,0;
    end
    
    local MB = GetSpellInfo(8092); -- Mind Blast
    local VT = GetSpellInfo(34914); -- Vampiric Touch
    
    if currentSpell == MB then --Mind Blast
        if isFotMSelected then
            insanityGain = (8) * 1.2;
        else
            insanityGain = 8;
        end
    elseif currentSpell == VT then --Vampric Touch
        insanityGain = 5;
    else
        insanityGain = 0;
        return 0,0,0,0;
    end
    
    if isS2MActive then
        insanityGain = insanityGain * 2.0;
    end
    
    local totalInsanityGain = math.floor(currentInsanity+insanityGain);
    
    return totalInsanityGain,maxInsanity,0,0;
end