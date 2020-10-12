local HorR;
if string.find(Var "Element", "Hold") then
	HorR = "hold";
else
	HorR = "roll";
end


if string.find(Var "Element", "Active") then
	return Def.Sprite {
		Texture=NOTESKIN:GetPath( '_UpLeft', HorR..'a' );
		Frames = Sprite.LinearFrames( 1, 1 );
	};
else
	return Def.Sprite {
		Texture=NOTESKIN:GetPath( '_UpLeft', HorR..'i' );
		Frames = Sprite.LinearFrames( 1, 1 );
	};
end
